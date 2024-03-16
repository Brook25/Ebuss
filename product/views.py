from django.shortcuts import render
from djano_redis import get_redis_connection
from django.http import JsonResponse 
from .serailizers import ProductSerializer
# Create your views here.

class Popular(View):

    def get(self, request, *args, **kwargs):
        # popular done deals
        # Implement celery here
        redis_client = get_redis_connection('default')
        popular_deals = redis_client.lrange('popular', 0, -1)
        # generting url from registered views and adding pagination
        url = reverse('popular-product', kwarg={'page': args[0] + 1})
        response = json.loads({'popular_deals': popular_deals, url: url}
        return JsonResponse(response, safe=True, status=200)
