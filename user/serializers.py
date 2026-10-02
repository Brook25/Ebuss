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
                'birth_date', 'country_code', 'phone_no', 'subscriptions', 'profile_image', 'background_image', 'description', 'is_supplier']
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


class SupplierProfileSerializer(UserProfileSerializer):
    customer_metric = serializers.SerializerMethodField()
    product_metric = serializers.SerializerMethodField()
    achievements = serializers.SerializerMethodField()

    def get_achievements(self, obj):
        if obj.achievements.exists():
            return obj.achievements.all()[:5]
        return []

    def get_product_metric(self, obj):
        product_metric = {}
        if self.product_metric:
            quarterly_metric = self.product_metric.get_quarterly_metric()
            product_metric['quarterly_metric'] = self.product_metric._metric_serializer(quarterly_metric)
            if self.is_owner:
                yearly_metric = self.product_metric.get_yearly_metric()
                product_metric['yearly_metric'] = self.product_metric._metric_serializer(yearly_metric)
        return product_metric

    def get_customer_metric(self, obj):
        customer_metric = {}
        if self.customer_metric:
            customer_metric['custommer_quarterly_total'] = self.customer_metric.get_quarterly_metric()
            if self.is_owner:
                customer_metric['recurrent_metric'] = self.customer_metric.get_recurrent_customers()
        return customer_metric

    class Meta:
        fields = UserProfileSerializer.Meta.fields + MetricsSerializer.Meta.fields + ['customer_metric', 'achievements']

    def __init__(self, *args, **kwargs):
        self.is_owner = kwargs.pop('is_owner', False)
        self.product_metric = kwargs.pop('product_metric', None)
        self.customer_metric = kwargs.pop('customer_metric', None)
        super().__init__(*args, **kwargs)

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
