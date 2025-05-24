from appstore import celery_app
from django_redis import get_redis_connection
from django.db.models import Q
import ast
from datetime import datetime
from supplier.models import Metrics
from .models import Product
from .utils import PopularityCheck
from supplier.models import Metrics
from product.models import SubCategory
from .serializers import ProductSerializer


@celery_app.task
def do_popularity_check():
    
    redis_client = get_redis_connection('default')
    popular_list = redis_client.lrange('popular', 0, -1)
    
    #product_id = product.id

    # pass threshold percentage values from redis cache to the first function
    #+ add kwargs to the next function that holds threshold values for various
    #+ timeframes
    #+ the last one is for conversion arguements that we will get from redis
    # certain elements of the list should be removed based on timestamp

    pipeline = redis_client.pipeline()

    if redis_client.exists('subcat_popularity_check'):
        print(redis_client.lrange('subcat_popularity_check', 0, -1))
        subcat_check = redis_client.lrange('subcat_popularity_check', 0, 19)
        pipeline.ltrim('subcat_popularity_check', 0, 19)
        pipeline.rpush('subcat_popularity_check', *subcat_check)
        pipeline.execute()

    else:
        subcat_check_order = SubCategory.objects.all().order_by('name').values('pk')
        all_subcat_ids = [subcat['pk'] for subcat in subcat_check_order]
        redis_client.lpush('subcat_popularity_check', all_subcat_ids[19:] + all_subcat_ids[:19])
        subcat_check = all_subcat_ids[:19]

    subcat_check = [int(pk.decode('utf-8')) for pk in subcat_check]
    print(subcat_check)
    metricdata_for_subcats = Metrics.objects.filter(product__sub_category__pk__in=subcat_check)
    popularity_check = PopularityCheck(metricdata_for_subcats, subcategory_ids=subcat_check, popular_list=popular_list)
    popular = popularity_check.find_popular()
 
    if popular: # This is supposed to serialize the product and store it in redis
        if redis_client.rpush('popular', popular):
            return (True, f"New products have been added to popular products cache")
        else:
            return (False, f"New products not successfully added to popular products cache")
    return (False, "No popular products found.")
