from rest_framework import serializers
from .models import Order


class OrderSerializer(serialzers.ModelSerializer):
    cart = serialiers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    billing = serialiers.SerializerMethodField()
    shipment = serialiers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'

    def get_cart(self, obj):
        if hasattr(obj, 'cart'):
            return { 'cart_id': obj.cart.id, 'cart_name': obj.cart.name }
        return None
    
    def get_product(self, obj):
        if hasattr(obj, product)
            return { 'product_id': obj.product.id, 'product_name': obj.product.name }

    
    def get_billing(self, obj):
        return { 'billing_id': obj.billing.id }
    
    def get_shipment(self, obj):
        return { 'shipment_id': obj.shipment.id}


class SerializeShipment(serializers.ModelSerializer):
    payment_method = serializers.MethodSerializerField()
    tracking_info = serializers.MethodSerializerField()

    class Meta:
        model = Shipment
        fields = '__all__'

    def get_payment_method(self, obj):
        if hasattr(obj, 'payment_method'):
            return { 'payment_method': obj.payment_method }
        else:
            return None

    def get_tracking_info(self, obj):
        if hasattr(obj, 'tracking_info'):
            return { 'tracking_info': obj.tracking_info }
        else:
            return None
