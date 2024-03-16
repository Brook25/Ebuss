from django.views import View
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from models import (Notification, History)
from serializers import UserSerializer
from datetime import datetime, timedelta
import json
# Create your views here.

class Notification(View):

        def get(self, request, *args, **kwargs):
            ix = 0 if not args.ix else args.ix 
            curr_date = datetime.now()
            pag_until = curr_date - timedelta(days=30)
            paginate = Paginator(Notification.objects.all().filter(user=request.user).
                                filter(created_at <= pag_until), 10)
            notifications = paginate(page=ix)
            serializer = UserSerializer(notifications, model=Notification, many=True)
            if serializer.is_valid()
                return JsonResponse(serializer.data, safe=True)
            return JsonResponse(serializer.error, status=501)


class History(View):

    def get(self,request, *args, **kwargs):
        ix = 0 if not args.ix else args.ix
        paginate = Paginator(History.object.all().filter(user=request.user, 20))
        history = paginate(page=ix)
        serializer = UserSerializer(history, model=Notification, many=True)
        if serializer.is_valid():
            return JsonResponse(serialzer.data, safe=True)
        return JsonResponse(serialzer.error, status=501)


class WishList(View):

    def get(self, request, *args, **kargs):
        wish_list = request.user.wish_list.all()
        serializer = UserSerializer(wish_list, model=Product, many=True)

        if serializer.is_valid():
            return JsonResponse(serializer.data, safe=True)
        return JsonResponse(serializer.error, status=501)


class Recommendations(View):

    def get(self, request, *args, **kwargs):
        pass


class Subscriptions(View):

    def get(self, request, *args, **kwargs):
        
        subscriptions = request.user.subscriptions.all()
        serializer = UserSerializer(subscriptions, model=User, many=True)
 
        if serializer.is_valid():
            return JsonResponse(serializer.data, safe=True)
        return JsonResponse(serialzer.error, status=501)


        

class Settings(View):

    def get(self, request, *args, **kwargs):

        settings = request.cookies.get('settings', None)

        if settings:
            settings = json.loads(settings)
            return JsonResponse(settings, safe=True)
        return JsonResponse("error: Page not found", status=404)
