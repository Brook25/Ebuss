from django.apps import AppConfig

class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'product'

    def ready(self):
        from django.dispatch import Signal
        product_app_started = Signal()
        product_app_started.send(sender=self.__class__)
        
