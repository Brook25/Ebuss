from django.dispatch import receiver

@receiver(post_save, sender=Product)
def update_inventory_add(sender, instance, created, **kwargs):
    pass
