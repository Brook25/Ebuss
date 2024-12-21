from django.urls import path
from .views import (SubCategoryView, TagView)

urlpatterns = [
        path('tag/<str:type>', TagView.as_view(), name='tag'),
        path('<str:type>/<int:index>/', SubCategoryView.as_view(), name='subcategory'),
        path('', SubCategoryView.as_view(), name='subcategory_post')
        ]
