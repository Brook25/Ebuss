from django.apps import AppConfig
from django.contrib.auth.signals import persist_data_to_db_from_sessions

class CartConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cart'

    def __init__(self):
        super().__init__(*args, **kwargs)
        from .signals import persist_data_to_db_from_sessions
        user_logged_out.connect(copy_data_from_sessions_to_db)


@receiver(user_logged_out)
def copy_data_from_sessions_to_db(sender, request, **kwargs):
    persist_data_to_db_from_sessions(sender, request, **kwargs)
