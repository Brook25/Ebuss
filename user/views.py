from django.views import View
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from order.models import (CartOrder, SingleProductOrder)
from product.models import Product
from user.models import Wishlist
from .models import (User, Notification)
from .serializers import NotificationSerializer
from user.serializers import (UserSerializer, WishListSerializer)
from order.serializers import (CartOrderSerializer, SingleProductOrderSerializer)
from datetime import datetime, timedelta
import json
from utils import SetupObjects
# Create your views here.



class NotificationView(View):

    def get(self, request, index, *args, **kwargs):
       
        curr_date = datetime.now()
        page_until = curr_date - timedelta(days=30)
        paginate = Paginator(Notification.objects.filter(user__username='emilyjim1', created_at__gte=page_until).all(), 10)
        paginated = paginate.page(index)
        notifications = list(paginated.object_list.values())
        Notification.objects.all().delete()
        User.objects.all().delete()
        serializer = NotificationSerializer(data=notifications, many=True)
        print(Notification.objects.all(), User.objects.all())
        if serializer.is_valid():
            print(serializer.data)
            return JsonResponse(serializer.data, safe=False)
        return JsonResponse(serializer.errors, status=501, safe=False)



class HistoryView(View):

    def get(self,request, index, *args, **kwargs):
        

        if type(index) is not int:
            return JsonResponse({
                'error': 'index should be integer type.'},
                safe=False,
                status=401
                )
        
        cartorders = CartOrder.objects.filter(user__username='emilyjim1').order_by('-date')
        cartorder_paginator = Paginator(cartorders, 20)
        paginate_cartorder = cartorder_paginator.page(index)
        paginated_cartorder = list(paginate_cartorder.object_list)
        singleproductorders = SingleProductOrder.objects.filter(user__username='emilyjim1').order_by('-date')
        singleproductorder_paginator = Paginator(singleproductorders, 20)
        paginate_singleproductorder = singleproductorder_paginator.page(index)
        paginated_singleproductorder = list(paginate_singleproductorder.object_list)
        serialized_carthistory = CartOrderSerializer(paginated_cartorder, many=True)
        serialized_singleproducthistory = SingleProductOrderSerializer(paginated_singleproductorder, many=True)
        
        singleproduct_history = serialized_singleproducthistory.data
        cartorder_history = serialized_carthistory.data 
        if serialized_carthistory.validated() and serialized_singleproducthistory.validated():
            return JsonResponse({ 'singleProductOrders': singleproduct_history,
                                'Cartorders': cartorder_history },
                                safe=False,
                                status=200)
        elif serialized_carthistory.errors:
            return JsonResponse({ 'error_type': 'cart_history_error', 'error': serialized_carthistory.errors }, status=501, safe=False)
        else:
            return JsonResponse({ 'error_type': 'singlehistory_error', 'error': serialized_singleproducthistory.errors }, status=501, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class WishListView(View):
    
    def get(self, request, *args, **kwargs):
        
        wish_list = Wishlist.objects.filter(created_by__username='emilyjim1').all()
        serializer = WishListSerializer(wish_list, many=True)

        #if serializer.is_valid():
        return JsonResponse(serializer.data, safe=False, status=200)
        return JsonResponse({ 'error': 'couldn\'t load wishlist'}, safe=False, status=501)

    
    def post(self, request, *args, **kwargs):
        
        #setup = SetupObjects()
        #setup.delete_all_objects()
        #setup.create_test_objects()
        print(Product.objects.all().values('id', 'name'))
        
        try:
            wishlist_data = json.loads(request.body).get('wishlist', {})
            product_id = wishlist_data.get('product_id', None)
            if product_id:
                product = Product.objects.filter(pk=product_id).first()
                user = User.objects.filter(username='emilyjim1').first()
                wishlist_obj, _ = Wishlist.objects.get_or_create(created_by=user)
                wishlist_obj.product.add(product)
                
                print(Wishlist.objects.all().values())
                return JsonResponse(data={
                    'data': None, 'message':
                    'wishlist succefully updated'
                    },
                    status=200, safe=False)
            else:
                return JsonResponse(data={
                    'data': None, 'message':
                    'wishlist not succefully updated, product not found'
                    },
                    status=501, safe=False)
        
        except json.JSONDecodeError as e:
                return JsonResponse(data={
                    'data': None, 'message': 'wishlist not succefully updated'
                    },
                    status=501, safe=False)


    def delete(self, request, *args, **kwargs):
        data = json.loads(request.body) or {}
        product_id = data.get('product_id', None)
        user = User.objects.filter(username='emilyjim1').first()
        if not product_id:
            user.wishlist_for.delete()
            return JsonResponse(data={
                'message':
                    'wishlist succefully deleted.'
                }, 
                status=200, safe=False)
        else:
            product = Product.objects.filter(pk=product_id).first()
            user.wishlist_for.product.remove(product)
            

            print(product.id, type(product.id))
            return JsonResponse(data={
                'product_id': product.id,
                'message':
                    'product succefully removed from wishlist.'
                }, 
                status=200, safe=False)

        return JsonResponse(data={
            'message':
                'Action not succefully completed.'
            }, 
            status=501, safe=False)

        

class Recommendations(View):

    def get(self, request, *args, **kwargs):
        pass


@method_decorator(csrf_exempt, name='dispatch')
class Recent(View):

    def get(self, request, *args, **kwargs):
        username = 'emilyjim1'
        recently_viewed = cache.get(username + ':recently_viewed')
        recently_viewed = json.dumps(recently_viewed)
        return JsonResponse(data={ 'data': recently_viewed }, status=200, safe=False)

    def post(self, request, *args, **kwargs):
        username = 'emilyjim1'
        try:
            newly_viewed = json.loads(request.body)
            if newly_viewed and type(newly_viewed) is list:
                recently_viewed = json.loads(cache.get(username + ':recently_viewed'))
                if 0 < len(newly_viewed) < 25:
                    range_to_stay = recently_viewed[:25 - len(newly_viewed)]
                    updated_recently_viewed = newly_viewed + range_to_stay
                    cache.set(username + ':recently_viewed', json.dumps(updated_recently_viewed))
                    data = {
                            'data': updated_recently_viewed[0],
                            'message': 'recently viewied successfuly updated'
                            }
                    return JsonResponse(data=data, status=200, safe=False)
                else:
                    return JsonResponse(data={
                        'data': None,
                        'message': 'Error: wrong number of recently viewed products.'}, safe=False, status=400)
            else:
                return JsonResponse(data={'data': None,
                    'message': 'Error: Wrong data type.'
                    }, status=400)
                        
        except json.JSONDecodeError as e:
            return JsonResponse(data={'data': None, 'message': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class Subscriptions(View):

    def get(self, request, index, *args, **kwargs):
        
        user = User.objects.filter(username='emilyjim1').first()
        subs = user.subscriptions.all()
        paginator = Paginator(subs, 30)
        paginated_subs = paginator.page(index)
        subs = paginated_subs.object_list         
        serialized_subs = UserSerializer(subs, many=True)
 
        return JsonResponse(data={'data': serialized_subs.data },
                status=200,
                safe=False)
        
        return JsonResponse(data={'data': None,
            'message': 'no subscriptions found'},
            safe=False, status=501)


    def post(self, request, *args, **kwargs):
        
        user = User.objects.filter(username='emilyjim1').first()
        data = json.loads(request.body) or {}
        sub = data.get('subscription', None)
        if sub and type(sub) is int:
            subscribed_to = User.objects.filter(pk=sub).first()
            user.subscriptions.add(subscribed_to)
            return JsonResponse(data={'data': sub, 'message': 'subscription succsefully added'}, status=200, safe=False)
        return JsonResponse(data={'data': None, 'message': 'subscription not succesfully added'}, status=200, safe=False)


        

class Settings(View):

    def get(self, request, *args, **kwargs):

        settings = request.cookies.get('settings', None)

        if settings:
            settings = json.loads(settings)
            return JsonResponse(settings, safe=True)
        return JsonResponse("error: Page not found", status=404)


class Profile(View):
    pass
