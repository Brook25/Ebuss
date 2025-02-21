from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (LogIn, RegisterView, GetToken)


urlpatterns = [
        path('signup', RegisterView.as_view(), name='register'),
        path('login', LogIn.as_view(), name='login'),
        path('token', GetToken.as_view(), name='token-obtain-pair'),
        ]
