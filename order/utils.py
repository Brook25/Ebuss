from django.http import HttpRequest
from appstore import celery_app as app
from .models import CartOrder
import hashlib
import hmac
import os
import requests

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
        order = CartOrder.objects.get(tx_ref)
        PG_VERIFICATION_URLS = {
            'chapa': f'https://api.chapa.co/v1/transaction/verify/{tx_ref}',
        
        }

        PG_PAYMENT_STATUS = {
            'chapa_success': ('success', 'in_progress'),
            'chapa_failed': ('failed', 'failed'),
        }

        url = PG_VERIFICATION_URLS.get(payment_gateway)

        response = requests.get(url=url, headers=HEADERS)

        if response.status_code == 200: 
            payment_status = response.data.get('data', {}).get('status', None)
            if payment_status == 'success':
                order.status = 'in_progress'
                order.payment_status = 'success'
                order.save()
                return {'http_request': 'sent', 'response_status_code': '200', 'transaction_status': 'success'}
            if data.staus
    
    except CartOrder.DoesNotExist as e:
        return {'http_request': 'Not sent.', 'response_status_code': None,
                 'transaction_status': 'failed',
                   'reason': 'No cart order object found for the given tx_ref.'}









def verify_hash_key(secret_key, payload, hash):
        
    hash_obj = hmac.new(secret_key.encode('utf-8'), payload, hashlib.sha256)
    generated_hash = hash_obj.hexdigest()

    if generated_hash != hash:
        return False
    return True

