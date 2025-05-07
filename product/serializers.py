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
    supplier = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    sub_category = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all())

    def __init__(self, *args, **kwargs):
        
        fields = ['id', 'name', 'supplier']
        simple = kwargs.pop('simple', False)
        self.Meta.fields = fields if simple else '__all__'
        super().__init__(*args, **kwargs)

    def create(self):
        with transaction.atomic():
            product = Product.objects.create(**self.validated_data)
            post_save(Product, product, '', 0, 0)

    def update(self, product, **kwargs):
        
        if not isinstance(product, Product):
            raise TypeError('product must be an instance of Product Model.')

        with transaction.atomic():
            old_quantity = product.quantity
            new_quantity = self.validated_data['quantity']
            inventory_update = kwargs.get('update_inventory', False)
            exclude_fields = ['id', 'subcategory', 'supplier']
            
            
            for k, v in self.validated_data.items():
                if k not in exclude_fields:
                    setattr(product, k, v)
            product.save()
        
            if inventory_update and new_quantity != old_quantity:
                reason = self.validated_data.get('reason', None)
                product.save()
                post_save(Product, product, reason, old_quantity)

        return product

    def bulk_validate_tags(self, *args, **kwargs):
        
        if type(self.validated_data) is dict:
            products = [self.validated_data] if isinstance(self.validated_data, dict) else self.validated_data
        
        subcategory_ids = set([product.get('subcat_id') for product in products if product.get('tags', {})])
        if subcategory_ids:
            subcategories = SubCategory.objects.filter(pk__in=subcategory_ids).prefetch_related('tags')
            subcategories = {subcat.id: set(subcat.tags.all().values_list('name')) for subcat in subcategories}
            
            invalid_products = {'amount': 0, 'data': [], 'error': 'Invalid tag key for specified suncategory.'}
            for product in products:
                subcat_id = product.get('subcategory_id')
                sc_tags = subcategories.get(subcat_id, set())
                product_tags = set(product.get('tags').keys())
                if not product_tags.issubset(sc_tags):
                    invalid_tags = product_tags.difference(sc_tags)
                    invalid_products['amount'] += 1
                    invalid_products['data'].append({'product_name': product['name'], 'subcat_id': subcat_id, 'tags': invalid_tags})
           
            if invalid_products['amount']:
                self._errors['invalid_products'] = invalid_products
                return False
        
        return True


    def validate_description(self, value):
        if 270 > len(value) > 1500:
            raise serializers.ValidationError('length of description must be between specified values.')
        return value


    def validate_tags(self, value):
        print(type(value))
        for v in value.values():
            if len(v) > 20:
                raise serializers.ValidationError('tag values must have less than 20 characters.')
        return value

    def create_tag_values(self, description):
    
        try:
            tag_values = []
            first_tag_index = description.index('#')
            tagged_description = description[first_tag_index + 1:]
            for token in tagged_description.split('#'):

                word = token.strip()
                if len(word) < 20 and ' ' not in word:
                    tag_values = tag_values + trimmed_token.split
            return tag_values

        except ValueError:
            return []
    
    
    def validate(self, attrs):

        tag_values = [v for v in attrs.get('tags', {}).values()]
        description_tags = self.create_tag_values(attrs.get('description', ''))
        tag_values = tag_values + description_tags
        attrs['tag_values'] = tag_values
        return attrs


    def bulk_create(self):

        with transaction.atomic():
            try:
                product_objs = [Product(**product_data) for product_data in self.validated_data]
                post_save(Product, product_objs, '', 0, 0, many=True)
            except Exception as e:
                return str(e)

    class Meta:
        model = Product
        extra_kwargs = {
                    'created_at': {'read_only': True}
                        }

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name']
