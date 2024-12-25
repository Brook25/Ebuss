from django.path import path
from views import (DashBoard, DashBoardDate, Store)

urlpatterns = [
        path('home/', DashBoard.as_view(), name='dashboard'),
        path('timeframe/<str: period>/', DashBoardDate.as_view(), name='dashboard_daily'),
        path('store/<index: int>/', Store.as_view(), name='store'),
        pah('inventory/<index: int>/', Inventory.as_view(), name='inventory')
        ]
