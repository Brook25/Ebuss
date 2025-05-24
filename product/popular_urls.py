from django.urls import path
from .views import Popular

urlpatterns = [
    path('<str:path>/', Popular.as_view(), name='product_popular')
    ]
