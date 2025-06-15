from django.http import HttpRequest
from appstore import celery_app as app
from .models import CartOrder, Transaction
from user.serializers import NotificationSerializer
from user.models import User, Notification
import hashlib
import hmac
import os
import requests
from django.utils import timezone
from .serializers import TransactionSerializer

SECRET_KEY = os.getenv('CHAPA_SECRET_KEY')

HEADERS = {
        'Authorization': f'Bearer {SECRET_KEY}',
        'Content-Type': 'application/json'
    }

def get_payment_payload(request, tx_ref, amount, phone_number, **kwargs):

    if not isinstance(request, HttpRequest):
        raise TypeError("request must be an instance of HTTPRequest")
    
    if not any(isinstance(arg, str) for arg in [tx_ref, amount, phone_number]):
        raise TypeError("All of tx_ref, amount and phone_number must be of type string.")
    
    if not (amount.is_digit() and phone_number.is_digit()):
        raise TypeError("Amount and phone_number must be of type string.")


    if not SECRET_KEY:
        raise ValueError("Secret key not set.")
    

    payload = {
        "amount": amount,
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

    return (payload, HEADERS)


@app.task()
def check_transaction_status(tx_ref, payment_gateway='chapa'):
    
    try:
        transaction = Transaction.objects.get(tx_ref=tx_ref)

        PG_VERIFICATION_URLS = {
            'chapa': f'https://api.chapa.co/v1/transaction/verify/{tx_ref}',
        }

        PG_PAYMENT_STATUS = {
            'chapa_success': 'success',
            'chapa_failed': 'failed',
            'chapa_pending': 'pending'
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
                update_data['status'] = PG_PAYMENT_STATUS[(f'{payment_gateway}_{payment_status}')]
                serializer = TransactionSerializer(transaction, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                return serializer.data
             
        
        else:
            update_data['status'] = 'failed'
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
                    
    except Transaction.DoesNotExist as e:
        return {'error': str(e)}









def verify_hash_key(secret_key, payload, hash):
        
    hash_obj = hmac.new(secret_key.encode('utf-8'), payload, hashlib.sha256)
    generated_hash = hash_obj.hexdigest()

    if generated_hash != hash:
        return False
    return True

