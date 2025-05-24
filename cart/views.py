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
        products_in_cart = cache.hget('cart', request.user__username, [])
        if products_in_cart and isinstance(cart_data, list):
            product = get_object_or_404(Product, pk=cart_data.get('product_id', None))
            if products_in_cache and isinstance(products_in_cache, list):
                if len(products_in_cache) == 10:
                    cart_data = {'user': request.user, 'status': 'active'}
                    active_cart = CartSerializer(data=cart_data)
                    if active_cart.is_valid():
                        created, active_cart = Cart.objects.get_or_create(**active_cart.validated_data)
                        if created:
                            cart_data = CartData.objects.create(cart=active_cart).product.add(*products_in_cart)
                        else:
                            cart_data = CartData.objects.get(cart=active_cart).product.add(*products_in_cart)
                        cache.hset('cache', request.user__username, json.dumps([]))
                        return Response({'message': 'product successfully added to cart.'}, status=status.HTTP_200_OK)
            products_in_cart.append(product.id)
            added = cache.hset('cart', request.user__username, json.dumps(products_in_cart))
            if added:
                return Response({'message': 'product succfully added'}, status=status.HTTP_200_OK)      
        return Response({'message': 'product not successfully added. Please check your product details'},
                            status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args,**kwargs):
        
        product_id = request.GET.get('product_id', None)
        if product_id and isinstance(product_id, int):
            cart = request.user.carts.filter(status='active').first()
            CartData.objects.filter(cart=cart, product__id=product_id).delete()
            return Response({'message': 'product successfully removed from cart.'},
                    status=status.HTTP_200_OK)
        return Response({'message': 'product data not sufficient.'},
                status=status.HTTP_400_BAD_REQUEST)
