from rest_framework import serializers
from .models import (Product, Category, SubCategory,
        Tag, Review)

class ProductSerializer(serializers.ModelSerializer):
    supplier = UserSerializer()
    sub_category = SubCategorySerialzer()
    review = ReviewSerializer(many=True)

    class Meta:
        model = Product
        fields = '__all__'

class CategorySerialzer(serialzers.ModelSerializer):
     
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
    product = ProductSerializer(many=True)

    class Meta:
        model = Review
        fields = '__all__'
