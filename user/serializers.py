from rest_framework import serializers
from .models import (Notification, History)
from cart.serialziers import CartSerializer

class UserSerializer(serializers.ModelSerialzier):
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'user_name']


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ['note', 'type', 'uri']

class HistorySerializer(serialziers.ModelSerializer):
    product = serialzers.SerialzierMethodField()

    class Meta:
        model = History
        fields = ['product', 'billing_address', 'payment_method', 'shippment_address']

    def get_product(self, obj):
        return { 'product_name': obj.product.name,
                 'supplier': obj.product.supplier
               }

class MetricsSerializer(serializers.ModelSerializer):
    product = serializers.MethodSerializerField()
    customer = serializers.MethodSerializerField()
    order = serializers.MethodSerializerField()

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

class InventorySerialzer(serialzers.ModelSerialzer):
    product = serializers.MethodSerializerField()
    
    class Meta:
        model = Inventory
        fields = ['date', 'product', 'adjustment', 'quantity_before', 'quantity_after', 'reason']

    def get_product(self, obj):
        return { 'product_name': obj.product.name,
                 'product_id': obj.product.id
               }

class WishListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = WishList
        fields = ['modified_at', 'product', 'priority']

    def get_product(self, obj):
        return obj.products.only('name', 'id')
