from appstore import celery_app

@celery_app.task
def sort_data(data, criterea):
    if criterea and data:
        pass
        # apply quick or heap sort or merge
