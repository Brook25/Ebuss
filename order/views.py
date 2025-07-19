from decimal import Decimal
from django.views import View
from django.core.cache import cache
from django.db import (transaction, IntegrityError)
from django.db.models import Prefetch
from functools import reduce
import json
import os
from cart.models import (Cart, CartData)
from product.models import Product
from .models import ( ShipmentInfo, CartOrder, Transaction)
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.permissions import (IsAuthenticated, AllowAny)
from rest_framework.response import Response
from rest_framework import status
from .serializers import (CartOrderSerializer, TransactionSerializer,
                          ShipmentSerializer)
from shared.utils import paginate_queryset
from .tasks import schedule_transaction_verification
from .utils import (get_payment_payload ,verify_hash_key)
import requests
import uuid
import time
from django.conf import settings
# Create your views here.

class OrderView(APIView):
    permission_classes = [IsAuthenticated]
    PAYMENT_TRANSACTION_URLS = {
        'chapa': "https://api.chapa.co/v1/transaction/initialize"
    }

    ASYNC_COUNTDOWN = 40

    def get(self, request, *args, **kwargs):
         
        cartOrders = CartOrder.objects.filter(user=request.user).select_related('cart').prefetch_related('cart__cart_data_for')
        cartOrders = paginate_queryset(cartOrders, request, CartOrderSerializer)
        
        return Response({'cart_orders': cartOrders.data}, status=status.HTTP_200_OK)

    def calc_total_amount(self, accumulator, cart_item):
        
        quantity = cart_item.get('quantity', 0)
        price = cart_item.get('product__price', Decimal('0.00'))

        total = quantity * price
        
        return accumulator + total
    
    def get_cart_data(self, cart_id):
        cart = Cart.objects.select_for_update().get(pk=cart_id)
        all_cart_data = CartData.objects.select_for_update().filter(cart=cart).values('product', 'product__price', 'quantity')
        return cart, all_cart_data
    
    def get_product_quantity_in_cart(self, all_cart_data):
        return {item['product']: item['quantity'] for item in all_cart_data}
    
    def get_order_data(self, request):
        order_data = request.data.get('order_data', None)
        if order_data:
            phone_number = order_data.get('phone_number', None)
            order_data['tx_ref'] = tx_ref = 'chapa-test-' + str(uuid.uuid4())
            cart_id = order_data.get('cart', None)
            return  order_data, phone_number, tx_ref, cart_id
    
    
    def get_payment_data(self, order_data, tx_ref, phone_number):
        payment_data = {
            "tx_ref": tx_ref,
            "amount": order_data['amount'],
            "phone_number": phone_number,
        }
        return payment_data

    def get_shipment_info_data(self, order_data):
        shipment_info_data = order_data.get('shipment_info', None)
        if shipment_info_data:
            return ShipmentSerializer(data=shipment_info_data)
        return None

    def get_cart_order_data(self, order_data):
        if order_data:
            return CartOrderSerializer(data=order_data)
        return None
    
    def create_transaction_data(self, tx_ref, order):
        if tx_ref and order:
            transaction_data = {
                'tx_ref': tx_ref,
                'order': order.pk,
                'total_amount': order.amount,
                'currency': 'ETB',
                'status': 'pending',
                'verification_attempts': 0,
                'last_verification_time': None,
                'payment_gateway_response': None
            }

            return TransactionSerializer(data=transaction_data)       


    def update_product_data(self, all_cart_data, product_quantity_in_cart):
        product_ids = [cart_data.get('product') for cart_data in all_cart_data]
        products = Product.objects.select_for_update().filter(pk__in=product_ids)

        for product in products:
            print(product.quantity)
            if product.quantity < product_quantity_in_cart[product.pk]:
                raise ValueError(f'Error: Not enough amount in stock for product {product.name}')
            #change this inot a bulk update
            product.quantity -= product_quantity_in_cart[product.pk]
            print(product.quantity)
        Product.objects.bulk_update(products, ['quantity'])
        

    def post(self, request, *args, **kwargs):
        
        try:
            order_data, phone_number, tx_ref, cart_id = self.get_order_data(request)
            if order_data:
                with transaction.atomic():
                    cart, all_cart_data = self.get_cart_data(cart_id)
                    order_data['amount'] = reduce(self.calc_total_amount, all_cart_data, Decimal('0.00'))
                    product_quantity_in_cart = self.get_product_quantity_in_cart(all_cart_data)

                    shipment_serializer = self.get_shipment_info_data(order_data)
                    if shipment_serializer.is_valid(raise_exception=True):
                        shipment_info = shipment_serializer.save()
                        order_data['shipment'] = shipment_info.pk
                        order_data['user'] = request.user.pk
                        order_data['cart'] = cart.pk

                    cart_order_serializer = self.get_cart_order_data(order_data)

                    if cart_order_serializer.is_valid(raise_exception=True):
                        order = cart_order_serializer.save()
                        self.update_product_data(all_cart_data, product_quantity_in_cart)
                        cart.status = 'inactive'
                        cart.save()
                    
                    transaction_serializer = self.create_transaction_data(tx_ref, order)
                    if transaction_serializer.is_valid(raise_exception=True):
                        transaction_serializer.save()
                    
                    payment_data = self.get_payment_data(order_data, tx_ref, phone_number)
                    payment_payload, headers = get_payment_payload(request, payment_data, cart_id)
                        
                    response = requests.post(self.PAYMENT_TRANSACTION_URLS.get('chapa'), json=payment_payload, headers=headers)
                        
                    if response.status_code == 200 and response.json().get('status', '') == 'success':
        
                        checkout_url = response.json().get('data', {}).get('checkout_url', None)
                        if checkout_url:
                            # call the celery task to start payment verification
                            schedule_transaction_verification.apply_async(args=[tx_ref, self.ASYNC_COUNTDOWN],
                                                                            countdown=self.ASYNC_COUNTDOWN)
                            return Response({'message': "Order succesfully placed and pending.",
                                    'checkout_url': checkout_url},
                                    status=status.HTTP_200_OK)
                            
                    return Response({'Error': 'checkout_url not provided from payment gateway.\
                                    Please try again.'},
                                status=status.HTTP_501_NOT_IMPLEMENTED)
                                
            return Response({'error': 'Order data not properly provided.'},
                             status=status.HTTP_400_BAD_REQUEST)

        except (IntegrityError, CartOrder.DoesNotExist, Cart.DoesNotExist, Product.DoesNotExist) as e:
            return Response({'Error': f'Unique constrains not provided for payment info. {str(e)}'},
                             status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except ValidationError as e:
            return Response({'Error': f'Error occured while validating your order. {str(e)}.'},
                            status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, type, id, *args, **kwargs):
        
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
            

class TransactionWebhook(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        
        PG_PAYMENT_STATUS = {
            'success': ('success', 'in_progress'),
            'failed/cancelled': ('failed', 'failed'),
            'refunded': ('refunded', 'failed'),
            'reversed': ('reversed', 'failed')
        }
        
        chapa_hash = request.headers.get('x-chapa-signature', None)

        if not chapa_hash:
            return Response('User not Authorzied to access this endpoint.', status=status.HTTP_401_UNAUTHORIZED)

        if not request.body:
            return Response('No payload data provided.', status=status.HTTP_400_BAD_REQUEST)
    
        secret_key = os.getenv('CHAPA_WEBHOOK_SECRET_KEY', None)

        if not secret_key:
            return Response('authorization couldn\'t be processed.', status.HTTP_501_SERVER_ERROR)
        
        if not verify_hash_key(secret_key, request.body, chapa_hash):
            return Response('User not Authorzied. Hash not valid', status=status.HTTP_401_UNAUTHORIZED)
        
        transaction_status = request.data.get('status', None)
        tx_ref = request.data.get('tx_ref', None)
        
        if transaction_status and tx_ref:
            payment_status, order_status = PG_PAYMENT_STATUS.get(transaction_status)
            with transaction.atomic():
                txn = Transaction.objects.get(tx_ref=tx_ref).select_related(
                    'order', 'order__cart'
                ).prefetch_related('order__cart__cart_data_for')
                
                txn.status = payment_status
                txn.response = json.loads(request.data)
                txn.save()
                txn.order.status = order_status
                txn.order.save()

                if transaction_status != 'success':
                    cart_product_data = {cart_data.product: cart_data.quantity for cart_data in txn.order.cart.cart_data_for}
                    with transaction.atomic():
                        products = Product.objects.select_for_update().get(pk__in=cart_product_data.values())
                        
                        for product in products:
                            product.quantity += cart_product_data[product.pk]
                            product.save()
                    
                    # log events here 

