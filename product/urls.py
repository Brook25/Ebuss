from django.urls import path
from .views import (ProductView, SubCategoryView, 
        CategoryView, Search)

urlpatterns = [
        path('<str:type>/<int:index>/', ProductView.as_view(), name='product'),
        path('<str:type>', ProductView.as_view(), name='product_post'),
        path('search/', Search.as_view(), name='product_search')
        ]
