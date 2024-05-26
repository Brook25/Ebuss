from django.views import View
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.core.cache import cache
from models import (Notification, History)
from serializers import UserSerializer
from datetime import datetime, timedelta
import json
# Create your views here.

class Notification(View):

    def get(self, request, *args, **kwargs):
        ix = args[0]
        curr_date = datetime.now()
        pag_until = curr_date - timedelta(days=30)
        paginate = Paginator(Notification.objects.filter(user=request.user).
                            filter(created_at <= pag_until), 10)
        notifications = paginate(page=ix)
        serializer = UserSerializer(notifications, model=Notification, many=True)
        if serializer.is_valid()
            return JsonResponse(serializer.data, safe=True)
        return JsonResponse(serializer.error, status=501)

class History(View):

    def get(self,request, *args, **kwargs):
        ix = args[0]
        paginate = Paginator(History.objects.filter(user=request.user, 20))
        history = paginate(page=ix)
        serializer = UserSerializer(history, model=Notification, many=True)
        if serializer.is_valid():
            return JsonResponse(serialzer.data, safe=True)
        return JsonResponse(serialzer.error, status=501)


class WishList(View):

    def get(self, request, *args, **kwargs):
        wish_list = request.user.wish_list.all()
        serializer = UserSerializer(wish_list, model=Product, many=True)

        if serializer.is_valid():
            return JsonResponse(serializer.data, safe=True, status=200)
        return JsonResponse(serializer.error, status=501)

    def post(self, request, *args, **kwargs):
        try:
            wishlist_data = json.loads(request.body)
            if wishlist_data:
                new_wishlist = wishlist_data.get('wish_list', [])
                user_wishlist = request.user.wishlist.products
                user_wishlist.append(new_wishlist)
                request.user.wishlist.save()
            
                return JsonResponse(data: {
                    'data': None, 'message':
                    'wishlist succefully updated'
                    },
                    status=200)
        
        except json.JSONDECODERROR as e:
                return JsonResponse(data: {
                    'data': None, 'message': 'wishlist not succefully updated'
                    },
                    status=501)


    def delete(self, request, *args, **kwargs):
        wishlist_ids = kwargs.get('ids', [])
        if wishlist_ids:
            request.user.wish_list.filter(wishlist__id__in=wishlist_ids).delete()
            return JsonResponse(data={
                message:{
                    'wishlist succefully deleted.'
                    }
                }, 
                status=200)
        

class Recommendations(View):

    def get(self, request, *args, **kwargs):
        pass


class ProductViews(view):

    def get(self, request, *args, **kwargs):

        if 'recent' in request.url:
            username = request.user.username
            recently_viewed = cache.hget(username, 'recently_viewed')
            recently_viewed = json.dumps(recently_viewed)
            return JsonResponse(data=recently_viewed, status=200, safe=True)

    def post(self, request, *args, **kwargs):

        if 'recent' in request.url:
            username = request.user.username
            try:
                newly_viewed = json.loads(request.body)
                if newly_viewed and type(newly_viewed) is list:
                    recently_viewed = json.loads(cache.hget(username, 'recently_viewed'))
                    if 0 < len(newly_viewed) < 25:
                        range_to_stay = recently_viewed[:25 - len(newly_viewed)]
                        updated_recently_viewed = newly_viewed + range_to_stay
                        cache.hset(username, 'recently_viewed', json.loads(updated_recently_viewed))
                        data = {data: updated_recently_viewed[0], message: 'recently viewied successfuly updated'}
                        return JsonResponse(data=json.loads(data), status=200, safe=True)
                    else:
                        return JsonResponse(data={data: None, message: 'Error: wrong number of recently viewed products.'}, status=400)
                else:
                    return JsonResponse(data={data: None, message: 'Error: Wrong data type.'}, status=400)
                        
            except json.JSONDECODERROR as e:
                return JsonResponse(data={data: None, message: str(e)}, status=400)


class Subscriptions(View):

    def get(self, request, *args, **kwargs):
        
        subscriptions = request.user.subscriptions.all()
        serializer = UserSerializer(subscriptions, model=User, many=True)
 
        if serializer.is_valid():
            return JsonResponse(serializer.data, safe=True)
        return JsonResponse(serialzer.error, status=501)


    def post(self, request, *args, **kwargs):
        
        subscribed_to = kwargs.get('subscribed_to', None)
        if subscribed_to and type(subscribed_to) is str:
            subscribed_to = User.objects.filter(id=subscribed_to)
            request.user.subscriptions.append(subscribed_to)
            request.user.save()
            # serialize data
            return JsonResponse()


        

class Settings(View):

    def get(self, request, *args, **kwargs):

        settings = request.cookies.get('settings', None)

        if settings:
            settings = json.loads(settings)
            return JsonResponse(settings, safe=True)
        return JsonResponse("error: Page not found", status=404)


class Profile(View):
    pass
