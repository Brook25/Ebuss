


class MetricsSerializer(serializers.ModelSerializer):
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
    month = serializers.PositiveIntegerField()
    count = serializers.PositiveIntegerField()
    total_purchases = serializers.PositiveIntegerField()

    class Meta(MetricSerializer):
        fields = MetricSerializer.Meta.fields + ['month', 'count', 'total_purchases']


class InventorySerialzer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    
    class Meta:
        model = Inventory
        fields = ['date', 'product', 'adjustment', 'quantity_before', 'quantity_after', 'reason']

    def get_product(self, obj):
        return { 'product_name': obj.product.name,
                 'product_id': obj.product.id
               }
