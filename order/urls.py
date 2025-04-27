from django.urls import path
from .views import (OrderView)

urlpatterns = [
        path('', OrderView.as_view(), name='order_view'),
        path('type/<int:id>', OrderView.as_view(), name='delete_order_view')
        ]
