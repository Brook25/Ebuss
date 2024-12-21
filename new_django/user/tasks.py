from celery import app as celery_app


@celery_app.app
def sort_data(data, criterea):
    if criterea and data:
        # apply quick or heap sort or merge
