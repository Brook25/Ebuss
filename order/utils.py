from django.http import HttpRequest
from django.urls import reverse
from appstore import celery_app as app
from .models import CartOrder, Transaction
from product.models import Product
from user.serializers import NotificationSerializer
from user.models import User, Notification
import hashlib
import hmac
import requests
import os
from django.utils import timezone
from .serializers import TransactionSerializer


def get_payment_payload(request: HttpRequest, data: dict, cart_id: int):
    """
    Validates payment information from a dictionary and returns a payload for Chapa API.
    """
    # Extract data
    amount = str(data.get('amount', ''))
    phone_number = data['phone_number'] if data.get('phone_number', None) else request.user.phone_number
    tx_ref = data.get('tx_ref')
    callback_url = f'https://sterling-primarily-lionfish.ngrok-free.app/webhook/tsx'
    return_url = f'https://sterling-primarily-lionfish.ngrok-free.app/home'


    # Validate data
    if not all([amount, phone_number, tx_ref]):
        raise ValueError("Missing required payment data.")

    if not amount.replace('.', '', 1).isdigit():
        raise ValueError("Amount must be a numeric string.")

    if not phone_number.isnumeric():
        raise ValueError("Phone number must be a numeric string.")

    # Get secret key and create headers
    secret_key = os.getenv('CHAPA_SECRET_KEY')
    if not secret_key:
        raise ValueError("Chapa secret key not configured.")

    headers = {
        'Authorization': f'Bearer {secret_key}',
        'Content-Type': 'application/json'
    }

    # Create payload
    user = request.user
    payload = {
        'amount': amount,
        'currency': 'ETB',
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone_number': phone_number,
        'tx_ref': tx_ref,
        'callback_url': callback_url,
        'return_url': return_url,
        'customization': {
            'title': f'Payment for {cart_id}',
            'description': f'user {request.user.username} has completed order for cart {cart_id}.'
        }
    }
    
    return payload, headers


def verify_hash_key(secret_key, payload, hash):
        
    hash_obj = hmac.new(secret_key.encode('utf-8'), payload, hashlib.sha256)
    generated_hash = hash_obj.hexdigest()

    if generated_hash != hash:
        return False
    return True

