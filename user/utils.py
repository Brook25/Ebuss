import jwt
from datetime import datetime
from django.conf import settings

SECRET_KEY = settings.SECRET_KEY

def generate_access_token(user):
        
    payload = {
        'user_id': user.pk,
        'username': user.username,
        'role': self.user.role,
        'exp': datetime.now() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
        'iat': datetime.now()
    }

    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def generate_refresh_token(user):
    
    payload = {
        'user_id': user.pk,
        'exp': datetime.utcnow() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
        'iat': datetime.now()
    }

    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

