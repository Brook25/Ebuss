from django.shortcuts import get_object_or_404
from django.core.cache import cache
from product.models import Product
from rest_framework.respose import Response
from rest_framwork.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import json
from .models import (Cart, CartData)
from .serializers import CartSerializer
from datetime import datetime
# Create your views here.

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        cart = get_object_or_404(Cart, user=request.user)
        serialized_cart = CartSerializer(cart)
        Response(serialized_cart.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
  
        cart_data  = request.data
        cart_in_cache = cache.hget('cart', request.user.username, [])
        validated_data = CartDataSerializer(data=cart_data)
        if cart_data and validated_data.is_valid():
            cart_in_cache.append(json.dumps(cart_data))
            cache.hset('cart', request.user.username, cart_in_cache)
            cart = Cart.objects.create(user=request.user, status='active')
            if len(products_in_cache) == 14:
                cart_in_cache = [json.dumps(cart.decode('utf-8')) for cart in cart_in_cache]
                cart_data_objs = CartData.objects.bulk_create([CartData(**cart) for cart in cart_in_cache])
            else:
                pass
                
                    return Response({'message': 'product successfully added to cart.'}, status=status.HTTP_200_OK)
        products_in_cart.append(product.id)
        added = cache.hset('cart', request.user__username, json.dumps(products_in_cart))
        if added:
            return Response({'message': 'product succfully added'}, status=status.HTTP_200_OK)      
        return Response({'message': 'product not successfully added. Please check your product details'},
                            status=status.HTTP_400_BAD_REQUEST)
   
    def put(self, request, *args, **kwargs):



    def delete(self, request, *args,**kwargs):
        
        product_id = request.GET.get('product_id', None)
        if product_id and isinstance(product_id, int):
            cart = request.user.carts.filter(status='active').first()
            CartData.objects.filter(cart=cart, product__id=product_id).delete()
            return Response({'message': 'product successfully removed from cart.'},
                    status=status.HTTP_200_OK)
        return Response({'message': 'product data not sufficient.'},
                status=status.HTTP_400_BAD_REQUEST)
