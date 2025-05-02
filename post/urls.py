from django.urls import path
from .views import (PostView, LikeView)

urlpatterns = [
        path('<str:post>/', PostView.as_view(), name='post'),
        path('<str:post>/<int:pk>/<str:path>/', LikeView.as_view(), name='post')
        ]
