from django.urls import path
from .views import CategoryView

urlpatterns = [
        path('<str:type>/<int:index>/', CategoryView.as_view(), name='category-view')
        ]
