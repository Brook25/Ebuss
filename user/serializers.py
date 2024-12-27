from rest_framework import serializers
from shared.serializers import BaseSerializer
from .models import (User, Notification, Wishlist)


class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.update(**validated_data)
        return instance

    def bulk_create(self, validated_data):
        product_objs = [Product(**product_data) for product_data in validated_data]

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username']



class NotificationSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    
    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, val in validated_data.items():
            if hasattr(instance, attr):
                setattr(instance, attr, val)
        instance.save()
    
    class Meta:
        model = Notification
        fields = ['id', 'uri', 'created_at', 'note', 'type']



class WishListSerializer(BaseSerializer):
    from product.serializers import ProductSerializer
    product = ProductSerializer(many=True)
    
    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, val in validated_data.items():
            if hasattr(instance, attr):
                setattr(instance, attr, val)
        instance.save()

    class Meta:
        model = Wishlist
        fields = ['created_by', 'modified_at', 'product', 'priority']
