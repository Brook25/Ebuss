from django.db import models
from datetime import date
from django.core.validators import MinValueValidator, MaxValueValidator
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
    price = DecimalField(max_digits=11, decimal_places=2)
    sub_category = ForeignKey('SubCategory', on_delete=models.CASCADE, related_name='products')
    date_added = DateField(default=date.today)
    quantity = PositiveIntegerField()
    tags = JSONField(default=dict)
    tag_values = ArrayField(CharField(max_length=50))  # Don't forget to add the product name in there
    rating = PositiveIntegerField(validators=[MaxValueValidator(5)])
    number_of_ratings = PositiveIntegerField()

    def __repr__(self):
        return '<Product> {}'.format(self.__dict__)


class Category(models.Model):
    name = CharField(max_length=30)


class SubCategory(models.Model):
    name = CharField(max_length=30)
    category = ForeignKey('Category', on_delete=models.CASCADE, related_name='sub_categories')
    tags = ManyToManyField('Tag', related_name='subcategories')


class Tag(models.Model):
    name = CharField(max_length=20)
    description = CharField(max_length=100)

class TokenToSubCategory():
    token = CharField(max_length=30)
    subcategories = ArrayField(CharField(max_length=50))


class SubCategorySearchWeight(models.Model):
    sub_category = ForeignKey('SubCategory', related_name='weight', on_delete=models.CASCADE)
    search_weight = PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    def __repr__(self):
        return '<{}> {}'.format(self.__class__.name, self.__dict__)

class Review(models.Model):
    product = ForeignKey('Product', on_delete=models.DO_NOTHING, related_name='reviews')
    review = TextField(validators=[check_vulgarity])
    rating = PositiveIntegerField()
    timestamp = DateTimeField(auto_now_add=True)

    def __repr__(self):
        return '<{}> {}'.format(self.__class__.__name__, self.__dict__)

