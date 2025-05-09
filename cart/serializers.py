from rest_framework import serializers
from cart.models import (Cart, CartData)
from product.serializers import ProductSerializer
from user.serializers import UserSerializer



class CartDataSerializer(serializers.ModelSerializer):
    product = ProductSerializer(simple=True)

    class Meta:
        model = CartData
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    cart_data_for = CartDataSerializer(many=True)
    
    class Meta:
        model = Cart
        fields = '__all__'

