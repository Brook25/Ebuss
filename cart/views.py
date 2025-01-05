from django.shortcuts import get_object_or_404, get_list_or_404
from django.views import View
from django.http import JsonResponse
from django.core.cache import cache
from product.models import Product
from rest_framework.respose import Response
from rest_framwork.views import APIView
from rest_framework import status
import json
from .models import Cart
from .serializers import CartSerializer
from datetime import datetime
# Create your views here.

class CartView(APIView):

    def get(self, request, *args, **kwargs):

        cart = get_object_or_404(user=request.user)
        serialized_cart = CartSerializer(cart)
        Response(serialized_cart.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
  
        cart_data = json.loads(request.body)
        cart = cache.hget('cart', request.user__username)
        if cart and isinstance(cart_data, list):
            get_list_or_404(Product, pk__in=[product.get('id', None) for product in cart_data])
            products_in_cache = json.loads(cache)
            if products_in_cache and isinstance(products_in_cache, list):
                if len(products_in_cache) == 10:
                    active_cache = CartSerializer(data={'user': request.user, 'status': 'active'})
                    if active_cache.is_valid():
                        
                    if not active_cache:

                    products_added = 
                products_in_cache += cart_data
                cart_updated = cache.hset('cart', request.user__username, json.dumps(products_in_cache))
                if not cart_updated:
                    return Response({'message': 'cart not successfully updated'}, status=status.501)

            request.session.save()
            return JsonResponse(data={'message': 'cart succefully added'}, status=200)
                else:
                    return JsonResponse(data={'message': 'cart name not provided'}, status=400)
            except json.JSONDecodeError:
                return JsonResponse(data={'message': 'json body not valid', status=400})
        return JsonResponse(data={'message': {'No cart data recieved.'}}, status=400)


    def delete(self, request, *args, **kwargs):
        pass