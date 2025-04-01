from django.contrib.auth import authenticate
from django.shortcuts import render
import jwt
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from user.serializers import UserSerializer
from user.models import User
from .utils import (generate_access_token, generate_refresh_token, generate_response)
# Create your views here.

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        new_user_data = request.data
        user = UserSerializer(data=new_user_data)

        if user.is_valid():
            user.create()
            
            return Response({'status': 'success'}, status=status.HTTP_200_OK)

        return Response({'status': 'error',
                                'error': user.errors},
                                status=status.HTTP_400_BAD_REQUEST)


class LogIn(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):

        username = request.data.get('username')
        password = request.data.get('password')
        print(username, password)
        user = User.objects.get(username=username)
        print(user.username, user.password)
        user = authenticate(request, username=username, password=password)
 
        if not user:
            return Response({'error': 'Invalid username or password'},
                    status=status.HTTP_401_UNAUTHORIZED)

        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)

        return generate_response(access_token, refresh_token)



class GetToken(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        
        refresh_token = request.COOKIES.get('refresh_token', None)

        if not refresh_token:
            return Response({'status': 'error', 'error': 'Refresh Token not provided.'},
                    status=status.HTTP_401_UNAUTHORIZED)
        
        algorithm = settings.SIMPLE_JWT.get('ALGORITHM')
        
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithm)
        except jwt.ExpiredTokenError:
            return Response({'status': 'error', 'error': 'Refresh token has expired. Log in with your credentials.'},
                    status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'status': 'error', 'error': 'Invalid Refresh Token'},
                    status=status.HTTP_401_UNAUTHORIZED)

        user = User.objects.filter(pk=payload.get('id')).first()

        if not user:
            return Response({'status': 'error', 'error': 'User not found'},
                    status=status.HTTP_401_UNAUTHORIZED)

        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)

        return generate_response(access_token, refresh_token)
