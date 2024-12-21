from django.path import path
from views import (DashBoard, DashBoardDate)

urlpatterns = [
        path('home/', DashBoard.as_view(), name='dashboard'),
        path('<str: period>/', DashBoardDate.as_view(), name='dashboard_daily',)
        ]
