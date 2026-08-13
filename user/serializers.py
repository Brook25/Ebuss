from rest_framework import serializers
from shared.serializers import BaseSerializer
from .models import (User, Notification, Wishlist)
from suppliers.metrics import CustomerMetrics
from django.conf import settings
import jwt 


SECRET_KEY = settings.SECRET_KEY


class UserSerializer(BaseSerializer):
    subscriptions = UserSerializer(many=True, simple=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password',
                'birth_date', 'country_code', 'phone_no', 'subscription', 'profile_image', 'background_image', 'description', 'is_supplier']
        extra_kwargs = {
            'email': {
                'write_only': True
            },
            'birth_date': {
                'write_only': True
            },
            'country_code': {
                'write_only': True
            },
            'password': {
                'write_only': True
            },
        }

    def create(self, **kwargs):
        User.objects.create_user(**self.validated_data)
    
    def __init__(self, *args, **kwargs):
        simple = kwargs.pop('simple', False)
        super().__init__(*args, **kwargs)
        if simple:
            self.Meta.fields = ['username', 'first_name', 'last_name', 'email', 'profile_image', 'is_supplier']



class UserProfileSerializer(UserSerializer, PostSerializer):
    products = ProductSerializer(many=True, simple=True, read_only=True)

    class Meta:           
        fields = UserSerializer.Meta.fields + PostSerializer.Meta.fields + ['products']


class SupplierProfileSerializer(UserProfileSerializer, MetricsSerializer):
    customer_metric = serializers.SerializerMethodField()
    achievements = serializers.SerializerMethodField()

    def get_achievements(self, obj):
        if obj.achievements.exists():
            return obj.achievements.all()[:5]
        return []

    def get_customer_metric(self, obj):
        return CustomerMetrics.get_customer_metrics(obj.user)

    class Meta:
        fields = UserProfileSerializer.Meta.fields + MetricsSerializer.Meta.fields + ['customer_metric', 'achievements']


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
