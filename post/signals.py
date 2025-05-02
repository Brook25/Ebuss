from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F
from .models import Comment


