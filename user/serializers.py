from rest_framework import serializers
from shared.serializers import BaseSerializer
from .models import (User, Notification, Wishlist)
from django.conf import settings
import jwt 


SECRET_KEY = settings.SECRET_KEY



class UserSerializer(BaseSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username']

    def generate_auth_tokens(self):
        
        payload = {
                'user_id': self.user.pk,
                'exp': datetime.utcnow() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
                }

        refresh_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        payload['username'] = self.user.username
        payload['role'] = self.user.role

        access_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return {
                'access_token': access_token,
                'refresh_token': refresh_token
                }

class NotificationSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    
    class Meta:
        model = Notification
        fields = ['id', 'uri', 'created_at', 'note', 'type']



class WishListSerializer(BaseSerializer):
    from product.serializers import ProductSerializer
    product = ProductSerializer(many=True)
    
    class Meta:
        model = Wishlist
        fields = ['created_by', 'modified_at', 'product', 'priority']
