from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from order.models import (CartOrder, SingleProductOrder)
from product.models import Product
from user.models import Wishlist
from shared.utils import paginate_queryset
from .models import (User, Notification)
from .serializers import NotificationSerializer
from user.serializers import (UserSerializer, WishListSerializer)
from order.serializers import (CartOrderSerializer, SingleProductOrderSerializer)
from datetime import datetime, timedelta
import json
from utils import SetupObjects
# Create your views here.



class NotificationView(APIView):

    def get(self, request, index, *args, **kwargs):
       
        curr_date = datetime.now()
        page_until = curr_date - timedelta(days=30)
        notifications = paginate_queryset(Notification.objects.filter(user__username='emilyjim1', created_at__gte=page_until).all(), request, 10, NotificationSerializer)
        
        return Response(serializer.data, status=status.HTTP_200_OK)



class HistoryView(APIView):

    def get(self, request, index, *args, **kwargs):
        
        products = Product.objects.only('id', 'name')
        cartOrders = CartOrder.objects.filter(user=request.user).order_by('-date').prefetch_related(Prefetch('product', queryset=products))
        cartOrders = paginate_queryset(cartorders, request, 20, CartOrderSerializer)
        
        singleProductOrders = SingleProductOrder.objects.filter(user=request.user).order_by('-date').select_related('product').only('id', 'name')
        serialized_singleProductOrders = paginate_queryset(singleProductOrders, request, 20, SingleProductOrderSerializer)
        
        return Response({ 'singleProductOrders': singleProductOrders,
                                'Cartorders': cartOrders },
                                status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class WishListView(APIView):
    
    def get(self, request, *args, **kwargs):
        try:
            wishlist = Wishlist.objects.get(user=User.objects.filter(username='emilyjoe1'))
            serialized_data = WishListSerializer(wishlist)
            return Response(serialized_data.data, status=status.HTTP_200_OK)
        except Wishlist.DoesNotExist:
            return Response({ 'error': 'couldn\'t load wishlist'}, status=404)

    
    def post(self, request, *args, **kwargs):
        
        try:
            wishlist_data = json.loads(request.body).get('wishlist', {})
            product_id = wishlist_data.get('product_id', None)
            if product_id:
                product = Product.objects.filter(pk=product_id).first()
                user = User.objects.filter(username='emilyjim1').first()
                wishlist_obj, _ = Wishlist.objects.get_or_create(created_by=user).prefetch_related('product')
                if product not in wishlist_obj.product.all():
                    wishlist_obj.product.add(product)
                
                return Response({
                    'message':
                    'wishlist succefully updated'
                    },
                    status=status.HTTP_200_OK)
            else:
                return Response({
                    'message':
                    'wishlist not succefully updated, product not found'
                    },
                    status=501)
        
        except json.JSONDecodeError as e:
                return Response({
                    'message': 'wishlist not succefully updated'
                    },
                    status=501)


    def delete(self, request, *args, **kwargs):
        data = json.loads(request.body) or {}
        product_id = data.get('product_id', None)
        user = User.objects.filter(username='emilyjim1').first()
        if not product_id:
            user.wishlist_for.delete()
            return Response({
                'message':
                    'wishlist succefully deleted.'
                }, 
                status=status.HTTP_200_OK)
        else:
            product = Product.objects.filter(pk=product_id).first()
            user.wishlist_for.product.remove(product)
            

            return Response({
                'product_id': product.id,
                'message':
                    'product succefully removed from wishlist.'
                },
                status=status.HTTP_200_OK)

        return Response({
            'message':
                'Action not succefully completed.'
            },
            status=501)

        

class Recommendations(APIView):

    def get(self, request, *args, **kwargs):
        pass


@method_decorator(csrf_exempt, name='dispatch')
class Recent(APIView):

    def get(self, request, *args, **kwargs):
        username = 'emilyjim1'
        recently_viewed = cache.get(username + ':recently_viewed')
        recently_viewed = json.dumps(recently_viewed)
        return Response({ 'data': recently_viewed }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        username = 'emilyjim1'
        try:
            newly_viewed = json.loads(request.body)
            if newly_viewed and isinstance(newly_viewed, list):
                recently_viewed = json.loads(cache.get(username + ':recently_viewed'))
                if 0 < len(newly_viewed) < 25:
                    range_to_stay = recently_viewed[:25 - len(newly_viewed)]
                    updated_recently_viewed = newly_viewed + range_to_stay
                    cache.set(username + ':recently_viewed', json.dumps(updated_recently_viewed))
                    data = {
                            'data': updated_recently_viewed[0],
                            'message': 'recently viewied successfuly updated'
                            }
                    return Response(data, status=200, safe=False)
                
                elif len(newly_viewed) == 25:
                    cache.set(username + ':recently_viewed', json.dumps(newly_viewed))
                    data = {
                            'data': newly_viewed[0],
                            'message': 'recently viewied successfuly updated'
                            }
                    return Response(data, status=200, safe=False)

                else:
                    return Response({
                        'message': 'Error: wrong number of recently viewed products.'},
                        safe=False, status=400)
            else:
                return Response(data={
                    'message': 'Error: Wrong data type.'
                    }, status=400)
                        
        except json.JSONDecodeError as e:
            return Response({'message': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class Subscriptions(APIView):

    def get(self, request, index, *args, **kwargs):
        
        user = User.objects.filter(username='emilyjim1').first()
        subs = user.subscriptions.all()
        serialized_subs = paginate_queryset(subs, request, 30, UserSerializer)
 
        if serialized_subs:
            return Response({'data': serialized_subs },
                status=status.HTTP_200_OK
                )
        
        return Response({
            'message': 'no subscriptions found'},
             status=404)


    def post(self, request, *args, **kwargs):
        
        user = User.objects.filter(username='emilyjim1').first()
        data = json.loads(request.body) or {}
        sub = data.get('subscription', None)
        if sub and isinstance(sub, int):
            subscribed_to = User.objects.filter(pk=sub).first()
        if subscribed_to:
            user.subscriptions.add(subscribed_to)
            return JsonResponse(data={'data': sub, 'message': 'subscription succsefully added'}, status=200)
        else:
            return JsonResponse(data={'message': 'subscription not succesfully added'}, status=404)


        

class Settings(APIView):

    def get(self, request, *args, **kwargs):

        settings = request.cookies.get('settings', None)

        if settings:
            settings = json.loads(settings)
            return JsonResponse(settings, safe=True)
        return JsonResponse("error: Page not found", status=404)


class Profile(APIView):
    pass
