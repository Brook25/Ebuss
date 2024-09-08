from rest_framework import serializers
from shared.serializers import BaseSerializer
from .models import (User, Notification,
        Metrics, Inventory, Wishlist)


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username']


class NotificationSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = Notification
        fields = ['id', 'uri', 'created_at', 'note', 'type']


class MetricsSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()

    class Meta:
        model = Metrics
        fields = ['quantity', 'product', 'customer', 'supplier', 'order', 'total_price']

    def get_customer(self, obj):
        return { 'customer_name': obj.customer.name,
                 'customer_id': obj.customer.id
               }

    def get_product(self, obj):
        return { 'product_name': obj.product.name,
                 'product_id': obj.product.id
               }
    def get_order(self, obj):
        return { 'order_id': obj.order.id }

class InventorySerialzer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    
    class Meta:
        model = Inventory
        fields = ['date', 'product', 'adjustment', 'quantity_before', 'quantity_after', 'reason']

    def get_product(self, obj):
        return { 'product_name': obj.product.name,
                 'product_id': obj.product.id
               }

class WishListSerializer(BaseSerializer):
    from product.serializers import ProductSerializer
    product = ProductSerializer(many=True)

    class Meta:
        model = Wishlist
        fields = ['created_by', 'modified_at', 'product', 'priority']
