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
    date_added = DateField(auto_now_add=True)
    quantity = PositiveIntegerField(blank=False)
    tags = JSONField(default=dict, blank=True)
    tag_values = ArrayField(CharField(max_length=50))  # Don't forget to add the product name in there
    rating = PositiveIntegerField(validators=[MaxValueValidator(5)], default=0)
    review = ManyToManyField('Review', related_name='reviewed_product')

    def __repr__(self):
        return '<Product> {}'.format(self.__dict__)


class Category(models.Model):
    name = CharField(max_length=30, null=False, blank=False)
    date_added = DateTimeField(auto_now=True)

class SubCategory(models.Model):
    name = CharField(max_length=30, null=False, blank=False)
    category = ForeignKey('Category', on_delete=models.CASCADE, related_name='sub_categories')
    tags = ManyToManyField('Tag', related_name='subcategories')
    date_added = DateTimeField(auto_now=True)


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
    timestamp = DateTimeField(auto_now_add=True)

    def validate_review_rating(self):
        if not (self.review and self.rating):
            raise ValidationError('both review and rating can\'t be null.')

    def clean(self):
        self.validate_review_rating()
        super().clean

    def __repr__(self):
        return '<{}> {}'.format(self.__class__.__name__, self.__dict__)

