from django.dispatch import receiver

@receiver(post_save, sender=Inventory)
def update_inventory(sender, instance, created, **kwargs):
    pass
