from django.contrib.auth.signals import user_logged_out
from celery import app as celery_app
from .models import Cart

@celery_app.task
def persist_data_to_db_from_sessions(user=None, carts=[]):
    try:
        if carts and user:
            carts = [cart.update({'user': user}) for cart in carts]
            Cart.objects.bulk_create(carts)
            #request.session['carts'] = {}
    except Exception as e:
        return "objects not added to db. (Error): " + e + "."
    return "objects succecfully persisted to db."
