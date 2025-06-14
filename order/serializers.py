from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from .models import (Cart, CartOrder, SingleProductOrder, BillingInfo, ShipmentInfo, Shipment)
from cart.models import (CartData, Cart)
from user.models import User
from cart.serializers import CartSerializer
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
            return ProductSerializer(obj.product, simple=True).data
        
        return None
    
class ShipmentSerializer(serializers.ModelSerializer):
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


class CartOrderSerializer(SingleProductOrderSerializer):
    cart = PrimaryKeyRelatedField(queryset=Cart.objects.all())
    cart_data = CartSerializer(source='cart', read_only=True)
    user = PrimaryKeyRelatedField(queryset=User.objects.all())
    billing = PrimaryKeyRelatedField(queryset=BillingInfo.objects.all())
    shipment = PrimaryKeyRelatedField(queryset=ShipmentInfo.objects.all())

    class Meta:
        model = CartOrder
        fields = '__all__'
