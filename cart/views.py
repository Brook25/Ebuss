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

    def post(self, path, request, *args, **kwargs):
  
        cart_data  = request.data
        if not cart_data:
            return Response({'error': 'product not successfully added. Please check your product details'},
                            status=status.HTTP_400_BAD_REQUEST)
        if path == 'create':
            cart = Cart.objects.create(user=request.user)
            cart_data = [{**cart_item, 'cart': cart.pk} for cart_item in cart_data]
            cart_to_cache = cart_data
        elif path == 'add':
            cart_to_cache = json.loads(cache.get(f'cart:{request.user.username}'))
            cart_id = cart_data.get('cart_id')
            cart_to_cache += cart_data
            
        serializer = CartDataSerializer(data=cart_data, many=True)
        if serializer.is_valid():
                cache.set(f'cart:{request.user.username}', cart_to_cache)
                serializer.bulk_create(cart_data)
                return Response({'cart_id': cart.pk, 'message':
                    'product successfully added to cart.'},
                    status=status.HTTP_200_OK
                    )
        Cart.objects.get('pk'=cart.pk).delete()
        return Response({'error': 'product not successfully added. Please check your product details'},
                            status=status.HTTP_400_BAD_REQUEST)
   
    def put(self, request, *args, **kwargs):
        cart_data  = request.data
        cart_id = cart_data.get('pk', None)
        if not (cart_data and cart_id):
            return Response({'error': 'cart id not provided.'},
                    status=status.HTTP_404_PAGE_NOT_FOUND)
        cart_in_cache = json.loads(cache.get(f'cart:{request.user.username}'))
        validated_data = CartDataSerializer(data=cart_data)
        if not validated_data.is_valid():
            return Response({'error': 'Wrong cart details provided.'})
        
        if path == 'update':
            for index, product in enumerate(cart_in_cache):
                if product.get('product') == validated_data.get('product'):
                    product['amount'] = validated_data.get('amount')
            if index == len(cart_in_cache):
                cart_in_cache.append(validated_data)
            if len(products_in_cache) % 10 == 0:
                cart_in_cache = CartData.objects.update_or_create()
                cart_data_objs = CartData.objects.bulk_create([CartData(**cart) for cart in cart_in_cache])

        

    def delete(self, request, *args,**kwargs):
        
        product_id = request.GET.get('product_id', None)
        if product_id and isinstance(product_id, int):
            cart = request.user.carts.filter(status='active').first()
            CartData.objects.filter(cart=cart, product__id=product_id).delete()
            return Response({'message': 'product successfully removed from cart.'},
                    status=status.HTTP_200_OK)
        return Response({'message': 'product data not sufficient.'},
                status=status.HTTP_400_BAD_REQUEST)
