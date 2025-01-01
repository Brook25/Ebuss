from django.db.models import post_save, post_delete
from django.dispatch import Signal

post_update = Signal()
