from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
#from cart.models import Cart
from product.models import Product
from shared.validators import check_vulgarity
from django.db.models import (
        CharField, DateField, EmailField,
        DateTimeField, ForeignKey, URLField,
        PositiveIntegerField, DecimalField, 
        ManyToManyField, TextField, IntegerField
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
        ('new_subscription', 'New subscrition'),
        ('product_update', 'Product update'),
        ('stock_related', 'stock related')
        )

class User(AbstractUser):
    email = EmailField(unique=True)
    country_code = CharField()
    phone_no = CharField(max_length=10, validators=[
        RegexValidator(regex=r'^[0-9]{10}$',
        message='Field must contain only numbers.',
        code='invalid_phone_number'
        )
    ])
    birth_date = DateField()
    last_modified = DateField(auto_now=True)
    subscriptions = ManyToManyField('User', symmetrical=False, related_name='subscribers')
    recommendations = ManyToManyField('product.Product', related_name='recommended_to') 

    REQUIRED_FIELDS = ['first_name', 'last_name', 'birth_date', 'phone_no']

    def __repr__(self):
        return '<User> firstname: {}, lastname: {}, username: {}, email: {}'.format(self.first_name, self.last_name, self.username, self.email)


class History(models.Model):
    cart = ForeignKey('cart.Cart', null=True, related_name='history', on_delete=models.CASCADE)
    product = ForeignKey('product.Product', null=True, related_name='history', on_delete=models.CASCADE)
    billing_address = CharField(max_length=70)
    payment_mmethod = CharField(max_length=20)
    shippment_address = CharField(max_length=70)

class Wishlist(models.Model):
    created_by = ForeignKey('User', related_name='wishlist_for', on_delete=models.CASCADE)
    created_at = DateTimeField(auto_now_add=True)
    product = ManyToManyField('product.Product', related_name='wishlists_in')
    priority = CharField(choices=PRIORITY_CHOICES, default='LOW')


class Notification(models.Model):
    user = ForeignKey('User', on_delete=models.CASCADE, related_name='notifications')
    created_at = DateTimeField(auto_now_add=True)
    note = TextField()
    type = CharField(choices=NOTIFICATION_TYPES)
    uri = URLField(max_length=200)

class Metrics(models.Model):
    product = ForeignKey('product.Product', on_delete=models.CASCADE, related_name='product_metrics')
    quantity = PositiveIntegerField(default=1)
    customer = ForeignKey('User', on_delete=models.CASCADE, related_name='customer_metrics')
    supplier = ForeignKey('User', on_delete=models.CASCADE, related_name='supplier_metrics')
    purchase_date = DateField(auto_now_add=True)
    order = ForeignKey('order.Order', on_delete=models.CASCADE, related_name='order_metrics')
    total_price = PositiveIntegerField()


class Inventory(models.Model):
    product = ForeignKey('product.Product', on_delete=models.CASCADE, related_name='inventory_changes')
    date = DateField(auto_now_add=True)
    adjustment = IntegerField(null=False)
    type = CharField(null=True)
    quantity_before = PositiveIntegerField()
    quantity_after = PositiveIntegerField()
    current_stoke = PositiveIntegerField()
    reason = CharField(max_length=255)
