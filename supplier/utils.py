import requests
from django.core.cache import cache
from django.core.exceptions import APIException
import os

TTL = 60 * 60 * 12 # 24 hours

def set_bank_data():
    
    banks_url = "https://api.chapa.co/v1/banks"
    secret_key = os.getenv('CHAPA_SECRET_KEY', None)
    if not secret_key:
        raise APIException('Chapa secret key not configured.')

    headers = {
    'Authorization': f'Bearer {secret_key}',
    'Content-Type': 'application/json'
    }

    response = requests.get(banks_url, headers=headers)

    data = response.data
    if not (response.status_code == 200 and data.get('message', None) == 'Banks retreived' and data.get('data', None)):
        raise APIException('Bank not identified on payment gateway. Try again.')

    bank_data = {bank['id']: bank for bank in bank_data}
    cache.set('bank_data', bank_data, TTL)
    return bank_data