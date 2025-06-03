from django.shortcuts import (get_object_or_404, get_list_or_404)
from django.db import transaction
from django.db.models import Q
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
        
        cart = get_list_or_404(CartData,
                Q(cart__user=request.user) &
                    Q(cart__status='active')
                )
        serialized_cart = CartDataSerializer(cart, many=True)
        cache.set(f'cart:{request.user.username}', json.dumps(serialized_cart.data), timeout=345600)
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
                cart_data = [{**prod, 'cart': cart.id} for prod in request.data]
                serializer = CartDataSerializer(data=cart_data, many=True)
                
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    # Set initial cache
                    validated_data = [{'product': data['product'].pk,
                        'cart': data['cart'].pk,
                        'quantity': data['quantity']}
                        for data in serializer.validated_data]

                    cache.set(f'cart:{request.user.username}', json.dumps(validated_data), timeout=345600)
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
        
        data_type_validation = all([isinstance(cart, int), isinstance(product, int), isinstance(quantity, int)])

        if not all([cart, product, quantity]) and isinstance(cart, int) and data_type_validation:
            return Response(
                {'error': 'Missing required fields: cart_id, product_id, and amount are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart = get_object_or_404(Cart, pk=cart, user=request.user)
        
        if cart.status != 'active':
            return Response(
                {'error': 'Cart not active or unauthorized user for specifid cart.'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            cart_data, created = CartData.objects.get(cart=cart, product__pk=product), False
        except CartData.DoesNotExist:
            cart_data, created = None, True
            
        serializer = CartDataSerializer(instance=cart_data, data={'cart': cart.pk,
            'product': product,
            'quantity': quantity
            })
    
        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart_in_cache_old = cache.get(f'cart:{request.user.username}')

        if not cart_in_cache_old:
            all_cart_data = cart.cart_data_for.all()
            cart_in_cache_old = CartDataSerializer(all_cart_data, many=True).data
        else:
            cart_in_cache_old = json.loads(cart_in_cache_old)
        
        try:
            with transaction.atomic():
                
                serializer.save()
                # Update cache
                cart_in_cache_new = cart_in_cache_old.copy()
                
                if created:
                    cart_in_cache_new.append({
                        'product': product,
                        'quantity': quantity,
                        'cart': cart
                    })
                else:
                    for item in cart_in_cache_new:
                        if item.get('product') == product:
                            item['quantity'] = quantity
                            break
                
                cache.set(f'cart:{request.user.username}', json.dumps(cart_in_cache_new), timeout=345600)

                return Response({
                    'message': 'Cart item updated successfully',
                    'cart_item': {
                        'product': product,
                        'quantity': quantity
                    }
                }, status=status.HTTP_200_OK)

        except Exception as e:
            # Restore old cache state if transaction fails
            cache.set(f'cart:{request.user.username}', json.dumps(cart_in_cache_old), timeout=345600)
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, *args,**kwargs):
        
        product = request.GET.get('product', None)
        cart = request.GET.get('cart', None)
            
        if not product or not cart:
            return Response(
                {'error': 'Both product_id and cart_id are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
            
        cart = get_object_or_404(Cart, pk=cart_data_id)
        if cart.user != request.user:
            return Response(
                {'error': 'Unauthorized access to this cart.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Store original cache state before any changes
        original_cache = cache.get(f'cart:{request.user.username}')
        try:
            with transaction.atomic():
                cart_data = get_object_or_404(CartData, cart=cart, product__id=product_id)
                cart_data.delete()
                
                # Update cache
                cart_in_cache = cache.get(f'cart:{request.user.username}')
                if cart_in_cache:
                    cart_in_cache = json.loads(cart_in_cache)
                    cart_in_cache = [item for item in cart_in_cache if item.get('product') != product_id]
                    cache.set(f'cart:{request.user.username}', json.dumps(cart_in_cache), timeout=345600)
                
                return Response(
                    {'message': 'Product successfully removed from cart.'}, 
                    status=status.HTTP_204_NO_CONTENT
                )
            
        except Exception as e:
            # Restore original cache state if anything fails
            if original_cache:
                cache.set(f'cart:{request.user.username}', original_cache, timeout=345600)
            return Response(
                {'error': f'An error occurred while removing the product: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
