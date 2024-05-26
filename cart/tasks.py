from django.contrib.auth.signals import user_logged_out
from django.dipatch import receiver
from celery import app as celery_app
from .models import Cart

@celery_app.task
def persist_data_to_db_from_sessions(sender, request, **kwargs):
    try:
        user = request.user
        cart_data = request.session.get('carts', {})
        if cart_data:
            carts = [{'user': user, 'cart_name': k, **v} for k,v in session_data.items()]
            Cart.objects.bulk_create(carts)
            request.session['carts'] = {}
    except Exception as e:
        return "objects not added to db. (Error): " + e + "."
    return "objects succecfully persisted to db."
