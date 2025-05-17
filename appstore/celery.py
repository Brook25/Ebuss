from celery import Celery
from celery.schedules import crontab
import django
import os


app = Celery('appstore')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appstore.settings')
django.settings()

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'popularity_checker': {
        'task': 'tasks.do_popularity_check',
        'schedule': crontab(minute=0, hour=0, day_of_month='*/10'),
    },
}
