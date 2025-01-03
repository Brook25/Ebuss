from celery_async import app as celery_app
from django_redis import get_redis_connection
import ast
from datetime import datetime
from supplier.models import Metrics
from .models import Product
from .utils import PopularityCheck
from supplier.models import Metrics
import json
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

    percentage_thresholds = pipeline.hmget('purchase_percentage_thresholds', *subcat_check_order[:19])
    total_purchase_thresholds = pipeline.hmget('total_purchase_thresholds', *subcat_check_order[:19])
    purchase_3drate_thresholds = pipeline.hmget('purchase_3drate_thresholds', *subcat_check_order[:19])
    purhcase_14drate_thresholds = pipeline.hmget('purchase_14drate_thresholds', *subcat_check_order[:19])
    purhcase_21drate_thresholds = pipeline.hmget('purchase_21drate_thresholds', *subcat_check_order[:19])
    wishlist_thresholds = pipeline.hmget('wishlist_thresholds', *subcat_check_order[:19])
    conversion_rate_thresholds = pipeline.hmget('conversion_rate_thresholds', *subcat_check_order[:19])
    pipeline.execute()

    popularity_thresholds = {
            'percentage_thresholds': percentage_thresholds,
                'total_purchase_thresholds': total_purchase_thresholds,
                    'purchase_3drate_thresholds': purchase_3drate_thresholds,
                        'purchase_14drate_thresholds': purchase_14drate_thresholds,
                            'purchase_21drate_thresholds': purchase_21drate_thresholds,
                                'wishlist_thresholds': wishlist_thresholds,
                                    'conversion_rate_thresholds': conversion_rate_thresholds
            }

    
    subcats_tobe_checked = Metrics.objects.filter(product__pk__in=subcat_check_order)
    popularity_check = PopularityCheck(subcats_tobe_checked, **popularity_thresholds)
    popular = popularity_check.find_popular()
 
    if popular: # This is supposed to serialize the product and store it in redis
        if redis_client.rpush('popular', popular):
            return (True, f"New products have been added to popular products cache")
        else:
            return (False, f"New products not successfully added to popular products cache")
    return (False, "No popular products found.")
