from django.views import View
from django.db import (transaction, IntegrityError)
from django.db.models import Prefetch
import json
from cart.models import (Cart, CartData)
from product.models import Product
from .models import (BillingInfo, ShipmentInfo, SingleProductOrder, CartOrder)
from rest_framework.views import APIView
from rest_framework.permissions import (IsAuthenticated)
from rest_framework.response import Response
from rest_framework import status
from .signals import (post_order, clear_cart)
from .serializers import (CartOrderSerializer, SingleProductOrderSerializer,
                          SerializeShipment)
from shared.utils import paginate_queryset
import requests
import uuid
import time
from django.conf import settings
# Create your views here.

class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
         
        products = Product.objects.select_related('supplier').only('pk', 'name', 'supplier__username')
        singleProductOrders = SingleProductOrder.objects.filter(user=request.user).order_by('-created_at').prefetch_related(Prefetch('product', queryset=products))
        singleProductOrders = paginate_queryset(singleProductOrders, request, SingleProductOrderSerializer)

        carts = Cart.objects.get(user=request.user, status='active').cart_data_for.all()
        cartOrders = CartOrder.objects.filter(user=request.user).select_related('cart').prefetch_related('cart__cart_data_for')
        cartOrders = paginate_queryset(cartOrders, request, CartOrderSerializer)
        
        return Response({'cart_orders': cartOrders.data,
                            'single_product_orders': singleProductOrders.data}, status=status.HTTP_200_OK)

    def post(self, request, type, *args, **kwargs):

        try:
            order_data = request.data
            order_model = CartOrder if type == 'cart' else SingleProductOrder
            parent_field = 'product' if type == 'single' else 'cart'
            if order_data:
                billing_info_data = order_data.get('billing_info', None)
                shipment_info_data = order_data.get('shipment_info', None)
                cart_id = order_data.get('cart_id', None)
                product_id = order_data.get('product_id', None)
                parent = Cart.objects.get(pk=cart_id) if type == 'cart' else Product.objects.get(pk=product_id)
                if all([billing_info_data, shipment_info_data, parent]):
                    new_billing_info = SerializeShipment(data=billing_info_data)
                    new_shipment_info = SerializeShipment(data=shipment_info_data)
                    if new_billing_info.is_valid() and new_shipment_info.is_valid():
                        with transaction.atomic():
                            product = Product.objects.select_for_update().get(pk=product_id)
                            new_billing_info = new_billing_info.create()
                            new_shipment_info = new_shipment_info.create()
                            order = model(parent_field=parent, billing_info=new_billing_info, shipment_info=new_shipment_info)
                            order.save()
                            post_save.send(Order, order, request.user)
                            clear_cart.send(Order)
                        return Response({'message': "Order succesfully placed."}, status=status.HTTP_200_OK)
                    
                message = 'Error: order failed, Please check order details.'
                return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Order data not sufficient.'}, status=status.HTTP_400_BAD_REQUEST)

        except (json.JsonDecoderError, ValueError, TypeError) as e:
            message = "Error: couldn't parse values recieved. " + str(e)
            return Response("Order successfully placed.", status=501)
            message = "Error: couldn't parse values recieved. " + str(e)
            return Response("Order successfully placed.", status=501)
        
        except (IntegrityError, Order.DoesNotExist) as e:
            return Response({'message': 'Unique constrains not provided for payment info.'}, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, type, id, *args, **kwargs):
        
        if type == 'single':

            with transaction.atomic():
                single_order = SingleProductOrder.objects.get(pk=id).select_related('product')
                if single_order:
                    quantity = single_order.quantity
                    single_order.product.quantity += quantity
                    single_order.product.save()
                    single_order.delete()
                else:
                    return Response('Order not found', status=status.HTTP_400_BAD_REQUEST)
                
        elif type == 'cart':

            with transaction.atomic():
                cart_order = CartData.objects.filter(cart__pk=id).prefetch_related('cart', 'product', 'quantity')
                if cart_order:
                    for cart_data in cart_order:
                        cart_data.product.quantity += cart_data.quantity
                        cart_data.product.save()
                    cart_order.delete()
                    cart_order.cart.delete()
                else:
                    return Response('Order not found', status=400)

        return Response('Order successfuly deleted.', status=status.HTTP_200_OK)
            

class CheckOut(APIView):
    permission_classes = [IsAuthenticated()]
    
    def post(request, *args, **kwargs):
        
        phone_number = request.data.get('phone_no', None)
        if not phone_number:
            phone_number = request.user.phone_no
        
        tx_ref = 'chapa-test-' + uuid.uuid4()

        url = "https://api.chapa.co/v1/transaction/initialize"
        payload = {
            "amount": "10",
            "currency": "ETB",
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "phone_number": phone_number,
            "tx_ref": tx_ref,
            "callback_url": "https://webhook.site/077164d6-29cb-40df-ba29-8a00e59a7e60",
            "return_url": "https://www.google.com/",
            "customization": {
                "title": "Payment for my favourite merc",
                "description": "I love online payments"
            }
        }
        headers = {
            'Authorization': 'Bearer CHASECK-xxxxxxxxxxxxxxxx',
            'Content-Type': 'application/json'
        }
      
        response = requests.post(url, json=payload, headers=headers)
        data = response.text
