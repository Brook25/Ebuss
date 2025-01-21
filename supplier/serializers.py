from .models import (Inventory, Metrics)
from shared.serializers import BaseSerializer
from rest_framework import serializers

class MetricSerializer(BaseSerializer):
    product = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    iorder = serializers.SerializerMethodField()

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

class AnnotatedMetricSerializer(MetricSerializer):
    month = serializers.IntegerField(min_value=1)
    count = serializers.IntegerField(min_value=1)
    total_purchases = serializers.IntegerField(min_value=1)

    class Meta(MetricSerializer):
        fields = MetricSerializer.Meta.fields + ['month', 'count', 'total_purchases']


class InventorySerializer(BaseSerializer):
    product = serializers.SerializerMethodField()
    
    class Meta:
        model = Inventory
        fields = ['date', 'product', 'adjustment', 'quantity_before', 'quantity_after', 'reason']

    def get_product(self, obj):
        return { 'product_name': obj.product.name,
                 'product_id': obj.product.id
               }
