from django.http import HttpRequest
import hashlib
import hmac


def get_payment_payload(request, tx_ref, amount, phone_number, **kwargs):

    if not isinstance(request, HttpRequest):
        raise TypeError("request must be an instance of HTTPRequest")
    
    if not any(isinstance(arg, str) for arg in [tx_ref, amount, phone_number]):
        raise TypeError("All of tx_ref, amount and phone_number must be of type string.")
    
    if not (amount.is_digit() and phone_number.is_digit()):
        raise TypeError("Amount and phone_number must be of type string.")

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
    headers = {
        'Authorization': 'Bearer CHAPUBK_TEST-pjtmtdVDKoz81ExGys2m5BsprDlk18Ds',
        'Content-Type': 'application/json'
    }

    return (payload, headers)


def verify_hash_key(secret_key, payload, hash):
        
    hash_obj = hmac.new(secret_key.encode('utf-8'), payload, hashlib.sha256)
    generated_hash = hash_obj.hexdigest()

    if generated_hash != hash:
        return False
    return True

