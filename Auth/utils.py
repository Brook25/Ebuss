import jwt
from datetime import datetime
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import (AccessToken, RefreshToken)

SECRET_KEY = settings.SECRET_KEY

def generate_access_token(user):
        
    access_token_dj = AccessToken.for_user(user)
    
    return access_token_dj


def generate_refresh_token(user):
    
    refresh_token = RefreshToken.for_user(user)
    
    return refresh_token


def generate_response(access_token, refresh_token):
    
    response = Response({'status': 'success'}, status=status.HTTP_200_OK)
    response['Authorization'] = f'Bearer {access_token}'
    response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            samesite='Lax',
            max_age=1296000
            )

    return response
