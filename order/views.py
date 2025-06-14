from decimal import Decimal
from django.views import View
from django.db import (transaction, IntegrityError)
from django.db.models import Prefetch
from functools import reduce
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
from .utils import (get_payment_payload, verify_hash_key)
import requests
import uuid
import time
from django.conf import settings
# Create your views here.

class OrderView(APIView):
    permission_classes = [IsAuthenticated]
    PAYMENT_TRANASCTION_URLS = {
        'chapa': "https://api.chapa.co/v1/transaction/initialize"
    }

    def get(self, request, *args, **kwargs):
         
        products = Product.objects.select_related('supplier').only('pk', 'name', 'supplier__username')
        singleProductOrders = SingleProductOrder.objects.filter(user=request.user).order_by('-created_at').prefetch_related(Prefetch('product', queryset=products))
        singleProductOrders = paginate_queryset(singleProductOrders, request, SingleProductOrderSerializer)

        carts = Cart.objects.get(user=request.user, status='active').cart_data_for.all()
        cartOrders = CartOrder.objects.filter(user=request.user).select_related('cart').prefetch_related('cart__cart_data_for')
        cartOrders = paginate_queryset(cartOrders, request, CartOrderSerializer)
        
        return Response({'cart_orders': cartOrders.data,
                            'single_product_orders': singleProductOrders.data}, status=status.HTTP_200_OK)

    def calc_total_amount(self, accumulator, cart_item):
        
        quantity = cart_item.get('quantity', 0)
        price = cart_item.get('price', 0)

        total = quantity * price
        
        return accumulator + total
    
    
    def post(self, request, type, *args, **kwargs):
        
        try:
            order_data = request.data.get('order_data')
            if order_data:
                phone_number = request.data.get('phone_number', None)
                tx_ref = 'chapa-test-' + uuid.uuid4()
                cart_id = order_data.get('cart', None)
                cart = Cart.objects.get(pk=cart_id)
                all_cart_data = CartData.objects.filter(cart=cart).values('product', 'product__price', 'quantity')
                amount = reduce(self.calc_total_amount, all_cart_data, Decimal('0.00'))
                product_quantity_in_cart = {product: quantity for product, quantity in all_cart_data.items()}
                
                payment_payload, headers = get_payment_payload(request, tx_ref, amount, phone_number)

                billing_info_data = order_data.get('billing_info', None)
                shipment_info_data = order_data.get('shipment_info', None)
                if all([billing_info_data, shipment_info_data]):
                    new_billing_serializer = SerializeShipment(data=billing_info_data)
                    new_shipment_serializer = SerializeShipment(data=shipment_info_data)
                    cart_order = CartOrderSerializer(data=order_data)
                    if all([new_billing_serializer.is_valid(), new_shipment_serializer.is_valid(), cart_order.is_valid()]):
                        with transaction.atomic():
                            product_ids = [cart_data.get('product') for cart_data in all_cart_data]
                            products = Product.objects.select_for_update().filter(pk__in=product_ids)

                            for product in products:
                                product.quantity -= product_quantity_in_cart[product.pk]
                                product.save()

                            new_billing_serializer.save()
                            new_shipment_serializer.save()
                            cart_order.save()
                            cart.status = 'inactive'
                            cart.save()


                            response = requests.post(self.PAYMENT_TRANSACTION_URLS.get('chapa'), json=payment_payload, headers=headers)
                            
                            if response.status_code == 200:
                                redirect_url = response.json.get('redirect_url', None)
                                
                                if redirect_url:
                                    return Response({'message': "Order succesfully placed.",
                                          'redirect_url': redirect_url},
                                            status=status.HTTP_200_OK)
                    
                message = 'Error: order failed, Please check order details.'
                return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Order data not sufficient.'}, status=status.HTTP_400_BAD_REQUEST)

        except (json.JsonDecoderError, ValueError, TypeError) as e:
            message = "Error: couldn't parse values recieved. " + str(e)
            return Response("Order successfully placed.", status=501)
        
        except (IntegrityError, Order.DoesNotExist) as e:
            return Response({'Error': 'Unique constrains not provided for payment info.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_501_SERVER_ERROR)

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
        amount = request.data.get('amount', None)
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
            


