from rest_framework import serializers
from cart.models import (Cart, CartData)
from product.models import Product
from product.serializers import ProductSerializer
from user.models import User
from user.serializers import UserSerializer



class CartDataSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    cart = serializers.PrimaryKeyRelatedField(queryset=Cart.objects.all())

    class Meta:
        model = CartData
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    cart_data_for = CartDataSerializer(many=True)
    
    class Meta:
        model = Cart
        fields = '__all__'

