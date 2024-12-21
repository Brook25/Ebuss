from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment

@receiver(post_save, sender=Comment)
def increment_no_comments(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        post.comments += 1
        post.save()
