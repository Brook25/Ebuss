from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
import json
from models import Cart
import uuid
from serializers import BaseSerializer
from datetime import datetime
# Create your views here.

class CartView(View):

    def get(self, request, *args, **kwargs):

        cart_id = args[0]
        if cart_id and isinstance(cart_id, (int, str)):
            cart = Cart.objects.filter(id=cart_id)

        serialized_cart = BaseSerializer(model='Cart', fields=['id', 'timestamp', 'products'])
        if serialized_cart.is_valid():
            return JsonResponse(data=serialized_cart.data, safe=True)
        return JsonResponse(data=serialized_cart.error, status=501)

    def post(self, request, *args, **kwargs):
  
        if request.body:
            try:
                cart_data = json.loads(request.body)
                cart_name = cart_data['name']
                if cart_name:
                    carts = request.session.get('carts', {})
                    carts[cart_data.pop('name')] = cart_data
                    request.session.save()
                    return JsonResponse(data={'message': 'cart succefully added'}, status=200)
                else:
                    return JsonResponse(data={'message': 'cart name not provided'}, status=400)
            except json.JSONDecodeError:
                return JsonResponse(data={'message': 'json body not valid', status=400})
        return JsonResponse(data={'message': {'No cart data recieved.'}}, status=400)
