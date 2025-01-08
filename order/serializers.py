from rest_framework import serializers
from .models import CartOrder, SingleProductOrder, Shipment
from product.serializers import ProductSerializer
from shared.serializers import BaseSerializer
from user.serializers import UserSerializer

class SingleProductOrderSerializer(BaseSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = SingleProductOrder

    def get_user(self,obj):
        return UserSerializer(obj.user).data
    
    def get_product(self, obj):
        if hasattr(obj, 'product'):
            return ProductSerializer(data=obj.product, simple=True)
        
        return None
    


class CartOrderSerializer(SingleProductOrderSerializer):
    cart = serializers.SerializerMethodField()

    class Meta:
        model = CartOrder
        fields = '__all__'

    
    def get_cart(self, obj):
        if hasattr(obj, 'cart'):
            return { 'cart_id': obj.cart.id, 'cart_name': obj.cart.name }
        return None



class SerializeShipment(serializers.ModelSerializer):
    payment_method = serializers.SerializerMethodField()
    tracking_info = serializers.SerializerMethodField()

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
