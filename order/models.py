from django.db import models
from datetime import datetime
from django.core.validators import MinValueValidator, RegexValidator
from django.db.models import (
        CharField, DateField, EmailField,
        DateTimeField, ForeignKey, URLField,
        PositiveIntegerField, DecimalField, 
        ManyToManyField, TextField, IntegerField
        )

STATUS_TYPES = (
        ('in_progress', 'In Progress'),
        ('aborted', 'Aborted'),
        ('completed', 'Completed'),
        ('suspended', 'Suspended')
        )

# Create your models here.


class Order(models.Model):
    created_at = DateTimeField(default=datetime.now)
    order_status = CharField(max_length=30, default='pending')
   
    class Meta:
       abstract = True


    def __repr__(self):
        return '<Order> {}'.format(self.__dict__)



class CartOrder(Order):
    user = ForeignKey('user.User', on_delete=models.DO_NOTHING, related_name='cartorders_made')
    cart = ForeignKey('cart.Cart', on_delete=models.DO_NOTHING, related_name='cartorder_in')
    billing = ForeignKey('BillingInfo', on_delete=models.CASCADE, related_name = 'cart_order')
    shipment = ForeignKey('ShipmentInfo', on_delete=models.CASCADE, related_name = 'cart_order')

    class Meta:
        abstract = False

class SingleProductOrder(Order):
    user = ForeignKey('user.User', on_delete=models.CASCADE, related_name = 'singleproduct_orders')
    product = ForeignKey('product.Product', on_delete=models.DO_NOTHING, related_name='productorders_in')
    billing = ForeignKey('BillingInfo', on_delete=models.CASCADE, related_name = 'singleproduct_orders_in')
    shipment = ForeignKey('ShipmentInfo', on_delete=models.CASCADE, related_name = 'singleproduct_orders_in')
    
    class Meta:
        abstract = False


class Shipment(models.Model):
    contact_name = CharField(max_length=70, null=False)
    city = CharField(max_length=30, null=False)
    state = CharField(max_length=30, null=True)
    email_address = EmailField()
    address = CharField(max_length=70, null=False)
    phone_no = CharField(max_length=70, null=False, validators=[RegexValidator(regex=r'^[0-9]{10}$',
        message='Field must contain only numbers.',
        code='invalid_phone_number')])


    class Meta:
        unique_together = (('contact_name', 'city', 'state', 'email_address', 'address', 'phone_no'))

    @classmethod
    def get_or_create_payment_data(cls, payment_data):
        payment_info = cls.objects.filter(**payment_data).first()
        if payment_info:
            return (payment_info.id, True)
        else:
            new_payment_info = cls(**payment_data).save()
            return (new_payment_info.id, False)

    def __repr__(self):
        return '<{}> {}'.format(self.__class__.__name__, self.__dict__)

class BillingInfo(Shipment):
    payment_method = CharField(max_length=30, null=False)

    def get_or_create_billing_info(self, payment_data):
        return super.get_or_create_payment_data(payment_data)

class ShipmentInfo(Shipment):
    tracking_info = CharField(max_length=100, null=False)

    def get_or_create_shipment_info(self, payment_data):
        return super.get_or_create_payment_data(payment_data)

class Payment(models.Model):
    user = ForeignKey('user.User', on_delete=models.CASCADE, related_name='payments')
    amount = DecimalField(validators=[MinValueValidator(1)], max_digits=11, decimal_places=2, null=False)
    created_at = DateTimeField(auto_now=True)
    status = CharField(max_length=30, choices=STATUS_TYPES)
