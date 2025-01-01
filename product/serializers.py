from django.db import transaction
from rest_framework import serializers
from .models import (Product, Category, SubCategory,
        Tag, Review)
from user.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, val in validated_data.items():
            if hasattr(instance, attr):
                setattr(instance, attr, val)
        instance.save()
        return instance

    def bulk_create(self, validated_data):
        product_objs = [Product(**product_data) for product_data in validated_data]

    class Meta:
        model = Category
        fields = '__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, val in validated_data.items():
            if hasattr(instance, attr):
                setattr(instance, attr, val)
        instance.save()
        return instance

    def bulk_create(self, validated_data):
        product_objs = [Product(**product_data) for product_data in validated_data]
    class Meta:
        model = SubCategory
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=True)

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, val in validated_data.items():
            if hasattr(instance, attr):
                setattr(instance, attr, val)
        instance.save()
        return instance

    def bulk_create(self, validated_data):
        product_objs = [Product(**product_data) for product_data in validated_data]
    class Meta:
        model = Review
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    supplier = UserSerializer()

    def create(self, validated_data):
        with transaction.atomic():
            product = Product.objects.create(**validated_data)
            post_save(Product, product, '', 0, 0)

    def update(self, product_data):
        
        with transaction.atomic():
            product = Product.objects.select_for_update.get(pk=product_id)
            previous_quantity = product.quantity
            new_quantity = validated_items.pop('quantity', previous_quantity)
     

            for k, v in validated_data.items():
                setattr(product, k, v)
            product.save()
            
            inventory_update = product_data.get('update_inventory', False)
            if inventory_update and new_quantity != old_quantity:
                product.quantity = new_quantity
                reason = product_data.get('reason', None)
                product.save()
                post_save(Product, product, reason, previous_quantity)

        return product

    def bulk_create(self, validated_data):
        
        with transaction.atomic():
            product_objs = [Product(**product_data) for product_data in validated_data]
            post_save(Product, product_objs, '', 0, 0, many=True)


    class Meta:
        model = Product
        fields = ['id', 'name', 'supplier', 'description']

class TagSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, val in validated_data.items():
            if hasattr(instance, attr):
                setattr(instance, attr, val)
        instance.save()
        return instance

    def bulk_create(self, validated_data):
        product_objs = [Product(**product_data) for product_data in validated_data]
    class Meta:
        model = Tag
        fields = ['id', 'name']
