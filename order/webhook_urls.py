from django.urls import path
from .views import TransactionWebhook

urlpatterns = [
        path('', TransactionWebhook.as_view(), name='transaction-webhook')
]
