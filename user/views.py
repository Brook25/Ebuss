from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import (status, viewsets)
from rest_framework.permissions import (IsAuthenticated, AllowAny)
from django.shortcuts import (get_list_or_404, get_object_or_404)
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from cart.models import CartData
from order.models import (CartOrder)
from product.models import (Product, SubCategory)
from product.serializers import SubCategorySerializer
from product.utils import get_populars
from post.models import Post
from supplier.models import Achievements
from user.models import Wishlist
from shared.permissions import IsAdmin
from shared.utils import (paginate_queryset)
from .models import (User, Notification)
from .serializers import NotificationSerializer
from supplier.metrics import (ProductMetrics, CustomerMetrics)
from user.serializers import (UserSerializer, WishListSerializer)
from order.serializers import (CartOrderSerializer)
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
        return Response({'subcats': subcats.data,
                            'popular_products': popular_products}, 
                                    status=status.HTTP_200_OK)


class NotificationView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request, index, *args, **kwargs):
       
        curr_date = datetime.now()
        page_until = curr_date - timedelta(days=30)
        notifications = get_list_or_404(Notification.objects.filter(user=request.user, created_at__gte=page_until).all())
        notifications = paginate_queryset(notifications, request, 20, NotificationSerializer)
        
        return Response(notifications.data, status=status.HTTP_200_OK)



class HistoryView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request, index, *args, **kwargs):
        
        cartOrders = get_list_or_404(CartOrder.objects.filter(
                user=request.user, cart__status='active').order_by('-created_at').prefetch_related(
                    Prefetch('cart__cart_data_for', queryset=CartData.objects.prefetch_related('cart__cart_data_for__product'))))
        cartOrders = paginate_queryset(cartOrders, request, CartOrderSerializer, 20)
        
        return Response({ 'Cartorders': cartOrders.data },
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
                wishlist_obj, created = Wishlist.objects.get_or_create(created_by=request.user).prefetch_related('product')
                if created or product not in wishlist_obj.product.all():
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
                    'message': f'wishlist not succefully updated: {e}'
                    },
                    status=status.HTTP_404_PAGE_NOT_FOUND)


    def delete(self, request, type, *args, **kwargs):

        product_id = json.data.get('product_id', None)
        if not product_id and type == 'w':
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
        recently_viewed = cache.get(username + ':recently_viewed', [])        
        return Response(recently_viewed, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        try:
            newly_viewed = request.data
            username = request.user.username
            if newly_viewed and isinstance(newly_viewed, list):
                recently_viewed = cache.get(username + ':recently_viewed', [])
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
        serialized_subs = paginate_queryset(subs, request, UserSerializer, 30)
 
        if serialized_subs:
            return Response(serialized_subs.data,
                status=status.HTTP_200_OK
                )
        
        return Response({
            'message': 'no subscriptions found'},
             status=status.HTTP_404_PAGE_NOT_FOUND)


    def post(self, request, *args, **kwargs):

        sub_id = request.data
        if isinstance(sub_id, int):
            subscribed_to = get_object_or_404(User, pk=sub_id)
            request.user.subscriptions.add(subscribed_to)
            return Response({'message': 'subscription succsefully added'}, status=status.HTTP_200_OK)
        
        return Response({'message': 'subscription not succesfully added'}, status=status.HTTP_404_PAGE_NOT_FOUND)
    
    def delete(self, request, *args, **kwargs):
        sub_id = request.data
        if isinstance(sub_id, int):
            subscribed_to = get_object_or_404(User, pk=sub_id)
            request.user.subscriptions.remove(subscribed_to)
            return Response({'message': 'subscription succsefully removed'}, status=status.HTTP_200_OK)
        
        return Response({'message': 'subscription not succesfully removed'}, status=status.HTTP_404_PAGE_NOT_FOUND)


class ProfileView(APIView):
     
     def get(self, request, id, *args, **kwargs):
        year = datetime.today().year
        merchant = User.object.get(pk=id)
        permission = 'super' if merchant == request.user else 'guest'
        
        try:
            customer_metrics = CustomerMetrics(year, merchant)
            product_metrics = ProductMetrics(merchant, datetime.today())
            posts = Post.objects.filter(user=request.user)[:5]
            products = Product.objects.filter(supplier=request.user)[:20]
            user_data = { 'background_image': merchant.background_image,
                            'description': merchant.description
                            }  
            data = { 'posts': posts, 'products': products,
                        'product_metric': {}, 'customer_metric': {},
                        'user_data': user_data
                         }
            
            if merchant.is_supplier:
                data['achievements'] = merchant.achievements.all()
                data['popular_ads'] = merchant.products.ads.all().order_by('-created_at')[:4]
                data['product_metric']['quarterly_total'] = product_metrics.get_quarterly_metric()
                data['customer_metric']['customer_total'] = customer_metrics.get_total_customers('quarterly')
            
            if permission == 'super':
                data['customer_metric']['recurrent_metric'] = customer_metrics.get_recurrent_customers()
                data['product_metric']['yearly_metric'] = product_metrics.get_yearly_metric()
        
            return Response(data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'message': f'Data retreival failed: {e}'}, status=status.HTTP_404_PAGE_NOT_FOUND)
              