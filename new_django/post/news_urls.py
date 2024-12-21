from .views import News
from django.urls import path

urlpatterns = [
    path('<int:index>/', News.as_view(), name='news')
    ]
