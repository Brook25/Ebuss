from django.urls import path
from .views import (DashBoardHome, SupplierWalletView, DashBoardDate, Store, Inventory)

urlpatterns = [
        path('home/', DashBoardHome.as_view(), name='dashboard'),
        path('timeframe/<str:period>/', DashBoardDate.as_view(), name='dashboard_daily'),
        path('store/<int:index>/', Store.as_view(), name='store'),
        path('wallet/', SupplierWalletView.as_view(), name='supplier-wallet'),
        path('inventory/<int:index>/', Inventory.as_view(), name='inventory'),
        ]
