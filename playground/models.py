from django.db import models
from datetime import date, datetime
from django.contrib.auth.models import AbstractUser
from django.db.models import (
        CharField, IntegerField, TimeField, TextField, DecimalField,
        DateField, DateTimeField, BooleanField, EmailField, ForeignKey,
        OneToOneField, PositiveIntegerField, URLField,
        ImageField, ManyToManyField, OneToOneField
        )
from django.core.validators import  MaxValueValidator, RegexValidator
from .validators import vulgarity_validator 

# Create your models here.

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
    wish_list = ManyToManyField('Product', related_name='wish_lists_in')
    recommendations = ManyToManyField('Product', related_name='recommended_to') 

    REQUIRED_FIELDS = ['first_name', 'last_name', 'birthdate', 'phone_no']

    def __repr__(self):
        return '<User> firstname: {}, lastname: {}, username: {}, email: {}'.format(self.first_name, self.last_name, self.username, self.email)


class Product(models.Model):
    name = CharField(max_length=100, validators=[
        vulgarity_validator
        ])
    description = TextField()
    supplier = ForeignKey('User', on_delete=models.CASCADE, related_name='products')
    price = DecimalField(max_digits=11, decimal_places=2)
    sub_category = ForeignKey('SubCategory', on_delete=models.CASCADE, related_name='products')
    date_added = DateField(default=date.today)
    quantity = PositiveIntegerField()
    rating = PositiveIntegerField(validators=[MaxValueValidator(5)])
    number_of_ratings = PositiveIntegerField()

    def __repr__(self):
        return '<Product> {}'.format(self.__dict__)


class Category(models.Model):
    name = CharField(max_length=30)


class SubCategory(models.Model):
    name = CharField(max_length=30)
    category_id = ForeignKey('Category', on_delete=models.CASCADE, related_name='sub_categories')


class Order(models.Model):
    customer = ForeignKey('User', on_delete=models.CASCADE, related_name = 'orders')
    product = ForeignKey('Product', on_delete=models.DO_NOTHING)
    date = DateTimeField(default=datetime.now)
    quantity = PositiveIntegerField()
    billing_id = OneToOneField('BillingInfo', on_delete=models.CASCADE, related_name = 'order')
    shipment_id = OneToOneField('ShipmentInfo', on_delete=models.CASCADE, related_name = 'order')
    order_status = CharField(max_length=30, default='Pending')
    
    def __repr__(self):
        return '<Order> {}'.format(self.__dict__)


class Cart(models.Model):
    name = CharField(max_length=40, validators=[vulgarity_validator])
    customer = ForeignKey('User', on_delete=models.CASCADE, related_name='carts')
    timestamp = DateTimeField(auto_now=True)
    products = ManyToManyField('Product')

    def __repr__(self):
        return '<Cart> {}'.format(self.__dict__)


class PaymentAndShipment(models.Model):
    contact_name = CharField(max_length=70)
    city = CharField(max_length=30)
    state = CharField(max_length=30)
    email_address = EmailField()
    address = CharField(max_length=70)
    phone_no = CharField(max_length=70)

    def __repr__(self):
        return '<{}> {}'.format(self.__class__.__name__, self.__dict__)

class BillingInfo(PaymentAndShipment):
    payment_method = CharField(max_length=30)


class ShipmentInfo(PaymentAndShipment):
    tracking_info = models.CharField(max_length=100)


class History(models.Model):
    customer = ForeignKey('User', on_delete=models.CASCADE, related_name='purchase_history')
    supplier = ForeignKey('User', on_delete=models.DO_NOTHING, related_name='purchased_items_history')
    product_name = CharField(max_length=70)
    billing_address = CharField(max_length=70)
    payment_mmethod = CharField(max_length=20)
    shippment_address = CharField(max_length=70)


class Review(models.Model):
    product = ForeignKey('Product', on_delete=models.DO_NOTHING, related_name='reviews')
    review = TextField(validators=[vulgarity_validator])
    timestamp = DateTimeField(auto_now_add=True)

    def __repr__(self):
        return '<{}> {}'.format(self.__class__.__name__, self.__dict__)


class Notification(models.Model):
    user = ForeignKey('User', on_delete=models.CASCADE, related_name='notifications')
    note = TextField()
    uri = URLField(max_length=200)

class Comment(models.Model):
    user = ForeignKey('User', on_delete=models.DO_NOTHING)
    text = TextField(validators=[vulgarity_validator])
    timestamp = DateTimeField(auto_now_add=True)
    likes = PositiveIntegerField()

    def __repr__(self):
        return '<{}> {}'.format(self.__class__name, self.__dict__)

class Reply(Comment):
   comment = ForeignKey('Comment', on_delete=models.CASCADE, related_name='replies_to')
   reply_to = ForeignKey('User', null=True, on_delete=models.DO_NOTHING)

class Post(Comment):
    #user = ForeignKey('User', on_delete=models.CASCADE, related_name='posts')
    image = ImageField(null=True, upload_to='Images/')

class Sold(models.Model):
    product = OneToOneField('Product', on_delete=models.DO_NOTHING, related_name='soldi_set')
    amount = PositiveIntegerField(default=1)
