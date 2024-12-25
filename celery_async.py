from celery import Celery
from celery.schedules import crontab


app = Celery('appstore')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'popularity_checker': {
        'task': 'tasks.popularity_check',
        'schedule': crontab(minute=0, hour=0, day_of_month='*/10'),
    },
}
