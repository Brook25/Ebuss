from rest_framework import serializers
from cart.serializers import Cart
from product.serializers import ProductSerializer

class CartSerializer(serializers.ModelSerializer):
    products = serializers.MethodSerializerField(many=True)

    class Meta:
        model = Cart
        fields = '__all__'

    def get_products(self, obj):
        return ProductSerializer(obj.products, many=True)
