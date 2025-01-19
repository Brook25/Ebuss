from django.db import transaction
from rest_framework import serializers
from user.models import User
from .models import (Product, Category, SubCategory,
        Tag, Review)
from shared.serializers import BaseSerializer
from user.serializers import UserSerializer
from .signals import post_save

class CategorySerializer(BaseSerializer):
    
    class Meta:
        model = Category
        fields = '__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer()

        
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

    def __init__(self, *args, **kwargs):
        
        fields = ['id', 'name', 'supplier', 'description']
        simple = kwargs.get('simple', False)
        self.Meta.fields = fields[:-1] if simple else fields
        super.__init__(*args, **kwargs)


    def create(self, validated_data):
        with transaction.atomic():
            product = Product.objects.create(**validated_data)
            post_save(Product, product, '', 0, 0)

    def update(self, product_data):
        
        with transaction.atomic():
            product_id = product_data.get('product_id')
            product = Product.objects.select_for_update.get(pk=product_id)
            old_quantity = product.quantity
            new_quantity = product_data.pop('quantity', old_quantity)

            for k, v in product_data.items():
                setattr(product, k, v)
            product.save()

            inventory_update = product_data.get('update_inventory', False)
            if inventory_update and new_quantity != old_quantity:
                product.quantity = new_quantity
                reason = product_data.get('reason', None)
                product.save()
                post_save(Product, product, reason, old_quantity)

        return product
    
    def validate(self, *args, **kwargs):
        def validate_tags(products):
            subcategory_ids = set([product.get('subcat_id') for product in products])
            subcategories = SubCategory.objects.filter(pk__in=subcategory_ids).prefetch_related('tags')
            subcategories = {subcat.id: set(subcat.tags.all().values_list('name')) for subcat in subcategories}
            for product in products:
                subcat_id = product.get('subcategory_id')
                sc_tags = subcategories.get(subcat_id, set())
                product_tags = set(product.get('tags').keys())
                if not product_tags.issubset(sc_tags):
                    return False
            return True
        
        products = self.data.get('products', [])
        if validate_tags(products):
            return super().validate(*args, **kwargs)
        return False

    
    def bulk_create(self, validated_data):

        with transaction.atomic():
            try:
                product_objs = [Product(**product_data) for product_data in validated_data]
                post_save(Product, product_objs, '', 0, 0, many=True)
            except Exception as e:
                return str(e)

    class Meta:
        model = Product
        extra_kwargs = {'supplier': {'read_only': True},
                        'subcategory': {'read_only': True}
                        }


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name']
