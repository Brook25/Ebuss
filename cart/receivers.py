from django.dispatch import receiver
from order.signals import clear_cart
from django.core.cache import cache

@receiver(clear_cart, sender=Order)
def post_Cartorder(sender, instance, user, **kwargs):
    cart = cache.hset('cart', user.username, json.loads([]))
    cart_instance = instance.cart
    cart.status = 'inactive'
    cart.save()

