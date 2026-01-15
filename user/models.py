from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.core.validators import (MaxValueValidator, MinValueValidator)
#from cart.models import Cart
from product.models import Product
from shared.validators import check_vulgarity
from django.db.models import (
        CharField, DateField, EmailField,
        DateTimeField, ForeignKey, URLField,
        PositiveIntegerField, DecimalField, OneToOneField,
        ManyToManyField, TextField, IntegerField, BooleanField
        )
# Create your models here.

PRIORITY_CHOICES = (
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
        )

NOTIFICATION_TYPES = (
        ('order_status', 'Order status'),
        ('post_update', 'Post update'),
        ('earnings', 'Earnings'),
        ('new_subscription', 'New subscrition'),
        ('product_update', 'Product update'),
        ('stock_related', 'stock related')
        )

ROLES = (
        ('customer', 'Customer'),
        ('supplier', 'Supplier'),
        ('admin', 'Admin')
        )


class User(AbstractUser):
    email = EmailField(unique=True, blank=False, null=False)
    country_code = PositiveIntegerField(validators=[MaxValueValidator(999)])
    phone_no = CharField(max_length=10, validators=[
        RegexValidator(regex=r'^[0-9]{10}$',
        message='Field must contain only numbers.',
        code='invalid_phone_number'
        )
    ], null=False, blank=False)
    birth_date = DateField(null=False)
    last_modified = DateField(auto_now=True)
    profile_image = models.ImageField(upload_to='profile_images/')
    background_image = models.ImageField(upload_to='background_images/')
    subscriptions = ManyToManyField('User', symmetrical=False, related_name='subscribers')
    description = TextField(null=True)
    recommendations = ManyToManyField('product.Product', related_name='recommended_to') 
    is_supplier = BooleanField(default=False)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'birth_date', 'phone_no']

    def __repr__(self):
        return '<User> firstname: {}, lastname: {}, username: {}, email: {}'.format(self.first_name, self.last_name, self.username, self.email)


class Wishlist(models.Model):
    created_by = OneToOneField('User', related_name='wishlist_for', on_delete=models.CASCADE)
    created_at = DateTimeField(auto_now=True)
    modified_at = DateTimeField(auto_now_add=True)
    product = ManyToManyField('product.Product', related_name='wishlists_in', blank=False)


class Notification(models.Model):
    user = ForeignKey('User', on_delete=models.CASCADE, related_name='notifications')
    created_at = DateTimeField(auto_now=True)
    note = TextField(blank=False, null=False)
    type = CharField(choices=NOTIFICATION_TYPES, null=False)
    uri = URLField(max_length=200, null=False)
    priority = CharField(choices=PRIORITY_CHOICES, default='LOW')

