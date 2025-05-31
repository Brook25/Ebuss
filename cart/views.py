from django.shortcuts import get_object_or_404
from django.db import transaction
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
        if not (request.data and isinstance(request.data, list) and all(isinstance(item, dict) for item in request.data)):
            return Response(
                {'error': 'Invalid product data format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # Create new cart
                cart = Cart.objects.create(user=request.user)
                
                # Prepare cart data with cart ID
                cart_data = [{**item, 'cart': cart.id} for item in request.data]
                
                # Validate and save cart items
                serializer = CartDataSerializer(data=cart_data, many=True)
                if serializer.is_valid():
                    serializer.save()
                    # Set initial cache
                    cache.set(f'cart:{request.user.username}', json.dumps(cart_data))
                    return Response({
                        'cart_id': cart.id,
                        'message': 'Cart created successfully with products',
                        'products': cart_data
                    }, status=status.HTTP_201_CREATED)
                
                # If validation fails, delete the cart
                cart.delete()
                return Response(
                    {'error': 'Invalid product data', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request, *args, **kwargs):
        cart_id = request.data.get('cart_id')
        product_id = request.data.get('product_id')
        amount = request.data.get('amount')

        if not all([cart_id, product_id, amount]):
            return Response(
                {'error': 'Missing required fields: cart_id, product_id, and amount are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # Lock the CartData row for update
                cart_data = CartData.objects.select_for_update().get(
                    cart_id=cart_id,
                    product_id=product_id,
                    defaults={'amount': amount}
                )
                
                # Update the amount
                cart_data.amount = amount
                cart_data.save()

                # Update cache
                cart_in_cache = json.loads(cache.get(f'cart:{request.user.username}') or '[]')
                for item in cart_in_cache:
                    if item.get('product_id') == product_id:
                        item['amount'] = amount
                        break
                else:
                    cart_in_cache.append({
                        'product_id': product_id,
                        'amount': amount
                    })
                
                cache.set(f'cart:{request.user.username}', json.dumps(cart_in_cache))

                return Response({
                    'message': 'Cart item updated successfully',
                    'cart_item': {
                        'product_id': product_id,
                        'amount': amount
                    }
                }, status=status.HTTP_200_OK)

        except CartData.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, *args,**kwargs):
        
        product_id = request.GET.get('product_id', None)
        if product_id and isinstance(product_id, int):
            cart = request.user.carts.filter(status='active').first()
            CartData.objects.filter(cart=cart, product__id=product_id).delete()
            return Response({'message': 'product successfully removed from cart.'},
                    status=status.HTTP_200_OK)
        return Response({'message': 'product data not sufficient.'},
                status=status.HTTP_400_BAD_REQUEST)
