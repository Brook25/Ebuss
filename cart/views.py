from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.cache import cache
from product.models import Product
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import json
from .models import (Cart, CartData)
from .serializers import (CartSerializer, CartDataSerializer)
from datetime import datetime
# Create your views here.

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        cart = cache.get(f'cart:{request.user.username}')
        
        if cart:
            cart = json.loads(cart)
            return Response(cart, status=status.HTTP_200_OK)
        
        cart = get_object_or_404(Cart, user=request.user)
        serialized_cart = CartSerializer(cart)
        cache.set(f'cart:{request.user.username}', json.dumps(serialized_cart.data))
        
        return Response(serialized_cart.data, status=status.HTTP_200_OK)

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
                
                # Validate and save cart items
                serializer = CartDataSerializer(data=request.data, many=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    # Set initial cache
                    cache.set(f'cart:{request.user.username}', json.dumps(serializer.validated_data))
                    return Response({
                        'cart_id': cart.id,
                        'message': 'Cart created successfully with products',
                        'products': cart_data
                    }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request, *args, **kwargs):
        
        cart = request.data.get('cart', None)
        product = request.data.get('product', None)
        quantity = request.data.get('quantity', None)

        if not all([cart, product, quantity]):
            return Response(
                {'error': 'Missing required fields: cart_id, product_id, and amount are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = CartDataSerializer(data={'cart': cart,
            'product': product,
            'quantity': quantity
            })

        if not serializer.is_valid():
            return Response(
                {'error': 'Missing required fields: cart_id, product_id, and amount are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            with transaction.atomic():
                
                product = Product.objects.get(pk=product)
                cart = Cart.objects.get(pk=cart)
                
                created, cart_data = CartData.objects.update_or_create(product=product,
                        cart=cart,
                        defaults={'quantity':
                            quantity}
                        )

                # Update cache
                cart_in_cache = json.loads(cache.get(f'cart:{request.user.username}'))
                print(cart_in_cache)
                if created:
                    cart_in_cache.append({
                        'product_id': product_id,
                        'quantity': quantity
                    })
                
                else:
                    for item in cart_in_cache:
                        if item.get('product') == product:
                            item['quantity'] = quantity
                            break
                
                cache.set(f'cart:{request.user.username}', json.dumps(cart_in_cache))

                return Response({
                    'message': 'Cart item updated successfully',
                    'cart_item': {
                        'product_id': product_id,
                        'quantity': quantity
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
