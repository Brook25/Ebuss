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
            print(json)
            return Response(cart, status=status.HTTP_200_OK)
        
        cart = get_list_or_404(CartData, cart__user__in=request.user)
        serialized_cart = CartDataSerializer(cart)
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
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart_in_cache_old = cache.get(f'cart:{request.user.username}')

        if not cart_in_cache_old:
            all_cart_data = Cart.objects.filter(pk=cart).cart_data_for.all()
            cart_in_cache_old = CartDataSerializer(all_cart_data, many=True).data
        else:
            cart_in_cache_old = json.loads(cart_in_cache_old)
        
        try:
            with transaction.atomic():
                
                created, cart_data = CartData.objects.update_or_create(
                        product=Product.objects.get(pk=product),
                        cart=Cart.objects.get(pk=cart),
                        defaults={'quantity': quantity}
                        )

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

        except CartData.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Restore old cache state if transaction fails
            cache.set(f'cart:{request.user.username}', json.dumps(cart_in_cache_old), timeout=345600)
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
