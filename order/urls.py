from django.urls import path
from .views import (OrderView, 

urlpatterns = [
        path('/', OrderView.as_view(), name='order_View'),
        path('/type/<int:id>', OrderView.as_View(), name='delete_order_view')
        ]
