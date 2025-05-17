from celery import app as celery_app
from django_redis import get_redis_connection
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
        subcat_check = pipeline.lrange('subcat_popularity_check', 0, 19)
        pipeline.ltrim('subcat_popularity_check', 0, 19)
        list_reordered = pipeline.rpush('subcat_popularity_check', subcat_check)
        pipeline.execute()
        pipeline.reset()

    else:
        subcats_check_order = SubCategory.objects.all().order_by('name').values('pk')
        subcat_check_order = [subcat['pk'] for subcat in subcat_check_order]
        pipeline.lpush('subcat_popularity_check', subcat_check_order[:19] + subcats_check_order[19:])

    pipeline.execute()
    
    subcats_tobe_checked = Metrics.objects.filter(product__subcategory__pk__in=subcat_check_order)
    popularity_check = PopularityCheck(subcats_tobe_checked, popular_list=popular_list)
    popular = popularity_check.find_popular()
 
    if popular: # This is supposed to serialize the product and store it in redis
        if redis_client.rpush('popular', popular):
            return (True, f"New products have been added to popular products cache")
        else:
            return (False, f"New products not successfully added to popular products cache")
    return (False, "No popular products found.")
