from django.http import HttpRequest
from appstore import celery_app as app
from .models import CartOrder, Transaction
from product.models import Product
from user.serializers import NotificationSerializer
from user.models import User, Notification
import hashlib
import hmac
import os
import requests
from django.utils import timezone
from .serializers import TransactionSerializer
from celery import shared_task

SECRET_KEY = os.getenv('CHAPA_SECRET_KEY')

HEADERS = {
        'Authorization': f'Bearer {SECRET_KEY}',
        'Content-Type': 'application/json'
    }

@shared_task
def schedule_transaction_verification(tx_ref, payment_gateway='chapa', countdown=60):
    """Schedule a transaction verification with countdown"""
    
    transaction = Transaction.objects.get(tx_ref=tx_ref)
    if transaction.status == 'pending':
    
        if countdown <= 960:
            check_transaction_status.delay(tx_ref=tx_ref)  # 16 minutes
            schedule_transaction_verification.apply_async(
                args=[tx_ref, payment_gateway],
                countdown=countdown * 2
            )

@shared_task
def check_transaction_status(tx_ref, payment_gateway='chapa'):
    
    try:
        transaction = Transaction.objects.get(tx_ref=tx_ref).select_related('order').prefetch_related('order__cart__cart_data_for')

        PG_VERIFICATION_URLS = {
            'chapa': f'https://api.chapa.co/v1/transaction/verify/{tx_ref}',
        }

        PG_PAYMENT_STATUS = {
            'chapa_success': ('success', 'in_progress'),
            'chapa_failed': ('failed', 'failed'),
        }

        url = PG_VERIFICATION_URLS.get(payment_gateway)
        response = requests.get(url=url, headers=HEADERS)
        response_data = response.json()

        # Common update data
        update_data = {
            'payment_gateway_response': response_data,
            'verification_attempts': transaction.verification_attempts + 1,
            'last_verification_time': timezone.now()
        }

        if response.status_code == 200: 
            payment_status = response_data.get('data', {}).get('status', None)
            if payment_status:
                update_data['status'], cart_status = PG_PAYMENT_STATUS[(f'{payment_gateway}_{payment_status}')]
                serializer = TransactionSerializer(transaction, data=update_data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                transaction.order.status = cart_status
                transaction.order.save()
                if payment_status != 'success':
                    
                    cart_product_data = {cart_data.product: cart_data.quantity for cart_data in transaction.order.cart.cart_data_for}
                    products = Product.objects.select_for_update().filter(pk__in=cart_product_data.values())
                    
                    for product in products:
                        product.quantity += cart_product_data[product.pk]
                        product.save()

                return serializer.data
              
        else:
            serializer = TransactionSerializer(transaction, data=update_data, partial=True)
            if serializer.is_valid():
                serializer.save()
            
            # get admin users and send them an alarming notification
            admins = User.objects.filter(is_superuser=True)
            message = response_data.get('message', '')
            
            notification_data = {
                'note': f'Transaction error has been recieved from {payment_gateway} on tx_ref {tx_ref} with status code {response.status_code}.\
                reponse message: {message}. Please check and fix it.',
                'type': 'order_status',
                'uri': 'http://localhost/nots/1',
                'priority': 'high'
            }
            
            notification = Notification.objects.create(**notification_data)
            
            for admin in admins:
                admin.notification_for.append(notification)
                admin.save()
            return serializer.data
                    
    except (Transaction.DoesNotExist, CartOrder.DoesNotExist) as e:
        return {'error': str(e)}


def verify_hash_key(secret_key, payload, hash):
        
    hash_obj = hmac.new(secret_key.encode('utf-8'), payload, hashlib.sha256)
    generated_hash = hash_obj.hexdigest()

    if generated_hash != hash:
        return False
    return True

