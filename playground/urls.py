from django.urls import path
from .views import Posts

#URLConf
urlpatterns = [
        path('news/posts/<int:offset>/', Posts.as_view())
        ]
