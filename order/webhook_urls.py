from django.urls import path
from .views import TransactionWebhook

urlpatterns = [
        path('payment-webhook/', TransactionWebhook.as_view(), name='transaction-webhook')
]
