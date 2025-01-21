from django.db import models
from datetime import date
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.contrib.postgres.fields import (ArrayField)
from django.db.models import (
        CharField, DateField, JSONField,
        DateTimeField, ForeignKey,
        PositiveIntegerField, DecimalField, 
        ManyToManyField, TextField
        )
from shared.validators import check_vulgarity
# Create your models here.

class Product(models.Model):
    name = CharField(max_length=100, validators=[
        check_vulgarity
        ])
    description = TextField()
    supplier = ForeignKey('user.User', on_delete=models.CASCADE, related_name='products')
    price = DecimalField(max_digits=11, decimal_places=2, null=False, blank=False, validators=[MinValueValidator(20)])
    sub_category = ForeignKey('SubCategory', on_delete=models.CASCADE, related_name='products')
    created_at = DateField(auto_now_add=True)
    quantity = PositiveIntegerField(blank=False)
    tags = JSONField(default=dict, blank=True)
    tag_values = ArrayField(CharField(max_length=50))  # Don't forget to add the product name in there
    rating = PositiveIntegerField(validators=[MaxValueValidator(5)], default=0)
    review = ManyToManyField('Review', related_name='reviewed_product')

    def __repr__(self):
        return '<Product> {}'.format(self.__dict__)


class Category(models.Model):
    name = CharField(max_length=30, null=False, blank=False, unique=True)
    created_at = DateTimeField(auto_now=True)

class SubCategory(models.Model):
    name = CharField(max_length=30, null=False, blank=False, unique=True)
    category = ForeignKey('Category', on_delete=models.CASCADE, related_name='sub_categories')
    tags = ManyToManyField('Tag', related_name='subcategories')
    created_at = DateTimeField(auto_now=True)
    popularity_ratio = DecimalField(default=0.1, validators=[MaxValueValidator(1)], decimal_places=1, max_digits=2)
    three_day_threshold = PositiveIntegerField(null=False)
    fourteen_day_threshold = PositiveIntegerField(null=False)
    twenty_one_day_threshold = PositiveIntegerField(null=False)
    wishlist_threshold = PositiveIntegerField(null=False)
    conversion_rate_threshold = PositiveIntegerField(null=False)
    rating_threshold = PositiveIntegerField(null=False)

class Tag(models.Model):
    name = CharField(max_length=20, null=False, blank=False)
    description = CharField(max_length=100)

class TokenToSubCategory(models.Model):
    token = CharField(max_length=30, null=False, blank=False)
    subcategories = ArrayField(CharField(max_length=50), default=list)


class SubCategorySearchWeight(models.Model):
    sub_category = ForeignKey('SubCategory', related_name='weight', on_delete=models.CASCADE)
    search_weight = PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=False)
    
    def __repr__(self):
        return '<{}> {}'.format(self.__class__.name, self.__dict__)

class Review(models.Model):
    user = ForeignKey('user.User', on_delete=models.CASCADE, related_name='reviews_made')
    product = ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    review = TextField(validators=[check_vulgarity, MinLengthValidator(1)], null=True)
    rating = PositiveIntegerField(null=True)
    created_at = DateTimeField(auto_now_add=True)

    def validate_review_rating(self):
        if not (self.review and self.rating):
            raise ValidationError('both review and rating can\'t be null.')

    def clean(self):
        self.validate_review_rating()
        super().clean

    def __repr__(self):
        return '<{}> {}'.format(self.__class__.__name__, self.__dict__)

