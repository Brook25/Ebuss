from django.urls import path
from .views import (OrderView, SupplierWalletView, TransactionWebhook)

urlpatterns = [
        path('', OrderView.as_view(), name='order_view'),
        path('type/<int:id>', OrderView.as_view(), name='delete_order_view'),
        path('supplier/wallet/', SupplierWalletView.as_view(), name='supplier-wallet'),
        path('payment-webhook/', TransactionWebhook.as_view(), name='transaction-webhook'),
]
