from rest_framework import serializers
from shared.serializers import BaseSerializer
from .models import (User, Notification, Wishlist)
from django.conf import settings
import jwt 


SECRET_KEY = settings.SECRET_KEY


class UserSerializer(BaseSerializer):

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password',
                'birth_date', 'country_code', 'phone_no']
        extra_kwargs = {
            'email': {
                'write_only': True
            },
            'birth_date': {
                'write_only': True
            },
            'country_code': {
                'write_only': True
            }
        }

    def create(self, **kwargs):
        User.objects.create_user(**self.validated_data)


class ProfileSerializer(BaseSerializer):

    class Meta:
        model = User            
        fields = ['username', 'first_name', 'last_name', 'email', 'password',
                'birth_date', 'country_code', 'phone_no']


class NotificationSerializer(BaseSerializer):
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
