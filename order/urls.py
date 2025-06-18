from django.urls import path
from .views import (OrderView, SupplierWalletView)

urlpatterns = [
        path('', OrderView.as_view(), name='order_view'),
        path('type/<int:id>', OrderView.as_view(), name='delete_order_view'),
        path('supplier/wallet/', SupplierWalletView.as_view(), name='supplier-wallet'),
]
