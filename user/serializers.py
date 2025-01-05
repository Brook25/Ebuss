from rest_framework import serializers
from shared.serializers import BaseSerializer
from .models import (User, Notification, Wishlist)


class UserSerializer(BaseSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username']



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
