from rest_framework import serializers
from .models import (Product, Category, SubCategory,
        Tag, Review)
from user.serializers import UserSerializer

class CategorySerialzer(serializers.ModelSerializer):
     
    class Meta:
        model = Category
        fields = '__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    category = CategorySerialzer()

    class Meta:
        model = SubCategory
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=True)

    class Meta:
        model = Review
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    supplier = UserSerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', 'supplier']


