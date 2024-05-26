from celery import app as celery_app
from django_redis import get_redis_connection
import ast
from .utils import calculate_purchase_percentage
from appstore.product import Metrics
import json
from serialzers import ProductSerializer

@celery_app.task
def do_popularity_check(prod_obj):

    if product.quanity < 1500:
        return

    redis_client = get_redis_connection('default')

    popular_list = redis_client.get('popular').decode('utf-8')
    popular_list = ast.literal_eval(popular_list)
    product_id = product.id

    if product.id in popular_list:
        return
    # pass threshold percentage values from redis cache to the first function
    #+ add kwargs to the next function that holds threshold values for various
    #+ timeframes
    #+ the last one is for conversion arguements that we will get from redis

    percentage = redis_client.hget('purchase_percentage_thresholds', product_id)

    popular =  calculate_purchase_percentage(prod_obj, percentage) or
                    calculate_purchase_rate(prod_obj, **{}) or
                        calculate_conversion_rate(prod_obj, **conversion_args)
                            or calculate_review(prod_obj, review)
 
    if popular: # This is supposed to serialize the product and store it in redis
        fields = ('name', 'image', 'description')
        serialized_product = ProductSerializer(prod_obj, model='Product', fields=fields)
        if serialized_product.is_valid():
            if redis_client.rpush('popular', json.dumps(serialized_data.data)):
                return f"{prod_obj.id} has been added to popular products cache"
            else:
                return f"couldn't add {prob_obj.id} to popular products cache"
    return "{product_id} not popular"
