import appstore
from appstore import celery
from product.tasks import do_popularity_check


do_popularity_check.delay()
