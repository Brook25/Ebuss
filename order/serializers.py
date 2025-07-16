from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from .models import (Cart, CartOrder, ShipmentInfo, Transaction)
from cart.models import (CartData, Cart)
from user.models import User
from cart.serializers import CartSerializer
from product.serializers import ProductSerializer
from shared.serializers import BaseSerializer
from user.serializers import UserSerializer

class ShipmentSerializer(BaseSerializer):

    class Meta:
        model = ShipmentInfo
        fields = '__all__'


class CartOrderSerializer(BaseSerializer):
    cart = PrimaryKeyRelatedField(queryset=Cart.objects.all())
    cart_data = CartSerializer(source='cart', read_only=True)
    user = PrimaryKeyRelatedField(queryset=User.objects.all())
    shipment = PrimaryKeyRelatedField(queryset=ShipmentInfo.objects.all())

    class Meta:
        model = CartOrder
        fields = '__all__'

class TransactionSerializer(BaseSerializer):
    order = PrimaryKeyRelatedField(queryset=CartOrder.objects.all())

    class Meta:
        model = Transaction
        fields = '__all__'
        extra_kwargs = {
                'ebuss_amount': {
                    'read_only': True,
                 },
                
                'supplier_amount': {
                    'read_only': True
                }
        }
