from django.views import View
from django.db import (transaction, IntegrityError)
from django.db.models import Prefetch
import json
import os
from cart.models import (Cart, CartData)
from product.models import Product
from .models import (BillingInfo, ShipmentInfo, SingleProductOrder, CartOrder, PaymentTransaction)
from rest_framework.views import APIView
from rest_framework.permissions import (IsAuthenticated)
from rest_framework.response import Response
from rest_framework import status
from .signals import (post_order, clear_cart)
from .serializers import (CartOrderSerializer, SingleProductOrderSerializer,
                          SerializeShipment)
from shared.utils import paginate_queryset
from .utils import verify_hash_key
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
            "callback_url": "https://sterling-primarily-lionfish.ngrok-free.app/webhook/tsx",
            "return_url": "https://sterling-primarily-lionfish.ngrok-free.app/home",
            "customization": {
                "title": "Payment for cart: {cart_id}",
                "description": "user {request.user.username} has completed order for cart {cart_id}."
            }
        }
        headers = {
            'Authorization': 'Bearer CHAPUBK_TEST-pjtmtdVDKoz81ExGys2m5BsprDlk18Ds',
            'Content-Type': 'application/json'
        }
      
        response = requests.post(url, json=payload, headers=headers)
        redirect_url = response.json.get('redirect_url', None)
        transaction_obj = PaymentTransaction(user=request.user, amount=amount, trx_ref=tx_ref)

        return Response({'payment_url': redirect_url}, status=status.HTTP_201_OK)

class TransactionWebhook(APIView):

    def post(self, request, *args, **kwargs):
        
        chapa_hash = request.headers.get('Chapa-Signature', None)

        if not chapa_hash:
            return Response('User not Authorzied to access this endpoint.', status=status.HTTP_401_UNAUTHORIZED)

        if not request.data:
            return Response('No payload data provided.', status=status.HTTP_400_BAD_REQUEST)
    
        secret_key = os.env.get('CHAPA_SECRET_KEY', None)

        if not secret_key:
            return Response('authorization couldn\'t be processed.', status.HTTP_501_SERVER_ERROR)

        if not verify_hash_key(secret_key.encode('utf-8'), request.body, chapa_hash):
            return Response('User not Authorzied. Hash not valid', status=status.HTTP_401_UNAUTHORIZED)
        
        transaction_status = request.data.get('status', None)
        
        if transaction_status == 'success':
            pass
            
            


