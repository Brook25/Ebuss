from django.urls import path
from .views import (PostView)

urlpatterns = [
        path('<str:post>/', PostView.as_view(), name='post'),
        ]
