from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import (IsAuthenticated, AllowAny)
from django.shortcuts import (get_list_or_404, get_object_or_404)
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from order.models import (CartOrder, SingleProductOrder)
from product.models import Product
from user.models import Wishlist
from shared.utils import (paginate_queryset, get_populars)
from .models import (User, Notification)
from .serializers import NotificationSerializer
from user.serializers import (UserSerializer, WishListSerializer)
from order.serializers import (CartOrderSerializer, SingleProductOrderSerializer)
from datetime import datetime, timedelta
import json
import jwt
from utils import SetupObjects
# Create your views here.


class HomeView(APIView):
    
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        subcats = paginate_queryset(SubCategory.objects.all(), request, 30, SubCategorySerializer)
        popular_products = get_populars('product')
        return Response("Hello user", status=status.HTTP_200_OK)


class NotificationView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request, index, *args, **kwargs):
       
        curr_date = datetime.now()
        print(request.user)
        print(request.user.notifications.all())
        page_until = curr_date - timedelta(days=30)
        notifications = get_list_or_404(Notification.objects.filter(user=request.user, created_at__gte=page_until).all())
        notifications = paginate_queryset(notifications, request, 20, NotificationSerializer)
        
        return Response(notifications.data, status=status.HTTP_200_OK)



class HistoryView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request, index, *args, **kwargs):
        
        products = Product.objects.only('id', 'name')
        cartOrders = get_list_or_404(CartOrder.objects.filter(
            user=request.user).order_by('-date').prefetch_related(
                Prefetch('product', queryset=products)))
        cartOrders = paginate_queryset(cartOrders, request, 20, CartOrderSerializer)
        
        singleProductOrders = get_list_or_404(SingleProductOrder.objects.filter(
            user=request.user).order_by('-date').select_related('product'))
        singleProductOrders = paginate_queryset(singleProductOrders, request, 20, SingleProductOrderSerializer)
        
        return Response({ 'singleProductOrders': singleProductOrders,
                                'Cartorders': cartOrders },
                                status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class WishListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        
        wishlist = get_object_or_404(Wishlist, created_by=request.user)
        serialized_data = WishListSerializer(wishlist)
        return Response(serialized_data.data, status=status.HTTP_200_OK)

    
    def post(self, request, *args, **kwargs):
        
        try:
            wishlist_data = request.data.get('wishlist', {})
            product_id = wishlist_data.get('product_id', None)
            if product_id:
                product = get_object_or_404(Product, pk=product_id)
                wishlist_obj, _ = Wishlist.objects.get_or_create(created_by=request.user).prefetch_related('product')
                if product not in wishlist_obj.product.all():
                    wishlist_obj.product.add(product)
                
                return Response({
                    'message':
                    'wishlist succefully updated'
                    },
                    status=status.HTTP_200_OK)
            return Response({
                'message':
                'wishlist not succefully updated, product not found'
                },
            status=status.HTTP_404_PAGE_NOT_FOUND)
        
        except json.JSONDecodeError as e:
                return Response({
                    'message': 'wishlist not succefully updated'
                    },
                    status=status.HTTP_404_PAGE_NOT_FOUND)


    def delete(self, request, type, *args, **kwargs):

        product_id = json.data.get('product_id', None)
        if not product_id and type == 'c':
            request.user.wishlist_for.delete()
            return Response({
                'message':
                    'wishlist successfully deleted.'
                }, 
                status=status.HTTP_200_OK)
        elif type == 'p':
            product = Product.objects.filter(pk=product_id).first()
            request.user.wishlist_for.product.remove(product)
            
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
            status=status.HTTP_400_PAGE_NOT_FOUND)


class Recommendations(APIView):

    def get(self, request, *args, **kwargs):
        pass


@method_decorator(csrf_exempt, name='dispatch')
class Recent(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        username = request.user.username
        recently_viewed = cache.get(username + ':recently_viewed')
        recently_viewed = json.dumps(recently_viewed)
        return Response({ 'data': recently_viewed }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        try:
            newly_viewed = json.data
            username = request.user.username
            if newly_viewed and isinstance(newly_viewed, list):
                recently_viewed = json.loads(cache.get(username + ':recently_viewed'))
                if 0 < len(newly_viewed) < 25:
                    range_to_stay = recently_viewed[:25 - len(newly_viewed)]
                    updated_recently_viewed = newly_viewed + range_to_stay
                    cache.set(username + ':recently_viewed', json.dumps(updated_recently_viewed))
                    data = {
                            'message': 'recently viewied successfuly updated'
                            }
                    return Response(data, status=status.HTTP_200_OK)
                
                elif len(newly_viewed) == 25:
                    cache.set(username + ':recently_viewed', json.dumps(newly_viewed))
                    data = {
                            'message': 'recently viewied successfuly updated'
                            }
                    return Response(data, status=status.HTTP_200_OK)

                else:
                    return Response({
                        'message': 'Error: wrong number of recently viewed products.'},
                        status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(data={
                    'message': 'Error: Wrong data type.'
                    }, status=400)
                        
        except json.JSONDecodeError as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class Subscriptions(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, index, *args, **kwargs):
        
        subs = get_list_or_404(request.user.subscriptions.all())
        serialized_subs = paginate_queryset(subs, request, 30, UserSerializer)
 
        if serialized_subs:
            return Response({'data': serialized_subs },
                status=status.HTTP_200_OK
                )
        
        return Response({
            'message': 'no subscriptions found'},
             status=status.HTTP_404_PAGE_NOT_FOUND)


    def post(self, request, *args, **kwargs):

        sub_id = json.data.get('subscription', None)
        if isinstance(sub_id, int):
            subscribed_to = get_object_or_404(User, pk=sub_id)
            request.user.subscriptions.add(subscribed_to)
            return Response({'message': 'subscription succsefully added'}, status=status.HTTP_200_OK)
        
        return Response({'message': 'subscription not succesfully added'}, status=status.HTTP_404_PAGE_NOT_FOUND)


class Settings(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):

        settings = request.cookies.get('settings', None)

        if settings:
            settings = json.data
            return Response(settings, status=status.HTTP_200_OK)
        return JsonResponse("error: Page not found", status=status.HTTP_404_PAGE_NOT_FOUND)


class Profile(APIView):
    pass

