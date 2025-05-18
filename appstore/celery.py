from celery import Celery
from celery.schedules import crontab
import django
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appstore.settings')
django.setup()

app = Celery('appstore')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

'''
app.conf.beat_schedule = {
    'popularity_checker': {
        'task': 'product.tasks.do_popularity_check',
        'schedule': crontab(minute=0, hour=0, day_of_month='*/10'),
    },
}
'''
