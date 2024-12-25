from django.urls import path
from .views import Timeline

urlpatterns = [
        path('<int:index>', Timeline.as_view(), name='timeline')
        ]
