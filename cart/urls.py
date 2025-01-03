from django.urls import path
from .models import Cart

urlpatterns = [
        path('', Cart.as_view(), name='cart_view')
        ]
