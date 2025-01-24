from django.contrib.auth import authenticate
from django.shortcuts import render
import jwt
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
# Create your views here.

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        new_user_data = request.data
        user = UserSerializer(data=new_user_data)

        if user.is_valid():
            user.create()
            access_token =  generate_access_tokens(),
            refresh_token =  generate_refresh_token()
            response =  Response({
                'status':'success'},
                status=status.HTTP_200_OK)
            
            response['Authorization'] = f'Bearer {access_token}'
            response.set_cookie('refresh_token',
                                refresh_token,
                                httpOnly=True,
                                samesite='Lax',
                                max_age=1296000
                                )

            return response

        return Response({'status': 'failed',
                                'error': user.error},
                                status=status.HTTP_400_BAD_REQUEST)


def LogIn(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):

        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({'error': 'Invalid username or password'},
                    status=HTTP_401_UNAUTHORIZED)

        access_token = get_access_token(user)
        refresh_token = get_refresh_token(user)

        jwt_token = {
                'access_token': access_token,
                'refresh_token': refresh_token
                }
        
        return Response(jwt_token, status=status.HTTP_200_OK)


class GetToken(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        
        refresh_token = request.data.get('refresh_token', None)

        if not refresh_token:
            return Response({'error': 'Refresh TOken not provided.'},
                    status=status.HTTP_401_UNAUTHORIZED)
        
        algorithm = settings.SIMPLE_JWT.get('ALGORITHM')
        
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithm)
        except jwt.ExpiredTokenError:
            return Response({'error': 'Refresh token has expired. Log in with your credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid Refresh Token'}, status=status.HTTP_401_UNAUTHORIZED)

        user = User.objects.filter(pk=payload.get('user_id')).first()

        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_401_UNAUTHORIZED)

        access_token = get_access_token(user)
        refresh_token = get_refresh_token(user)

        return Response({'access_token': access_token,
                            'refresh_token': refresh_token}, status=status.HTTP_200_OK)
