from django.db import models
from datetime import datetime
from django.core.validators import MinValueValidator, RegexValidator
from django.db.models import (
        CharField, DateField, EmailField,
        DateTimeField, ForeignKey, URLField,
        PositiveIntegerField, DecimalField, 
        ManyToManyField, TextField, IntegerField
        )
from django.utils import timezone
from user.models import User
from cart.models import Cart
from decimal import Decimal


PAYMENT_STATUS_TYPES = (
    ('success', 'Success'),
    ('reversed','Reversed'),
    ('refunded', 'Refunded'),
    ('failed', 'Failed')
)
ORDER_STATUS_TYPES = (
        ('pending', 'Pending'),
        ('aborted', 'Aborted'),
        ('success', 'Success'),
        ('failed', 'Failed')
        )

PAYMENT_GATEWAYS = (
    ('chapa', 'Chapa'),
)

# Create your models here.


class CartOrder(models.Model):
    user = ForeignKey('user.User', on_delete=models.DO_NOTHING, related_name='cartorders_made')
    cart = ForeignKey('cart.Cart', on_delete=models.DO_NOTHING, related_name='cartorder_in')
    shipment = ForeignKey('ShipmentInfo', on_delete=models.CASCADE, related_name = 'cart_order')
    amount = DecimalField(validators=[MinValueValidator(1)], max_digits=11, decimal_places=2, null=False)
    tx_ref = CharField(unique=True)
    created_at = DateTimeField(auto_now=True)
    updated_at = DateTimeField(auto_now_add=True)
    status = CharField(max_length=30, choices=ORDER_STATUS_TYPES, default='pending')
    

    def __repr__(self):
        return '<Order> {}'.format(self.__dict__)


class ShipmentInfo(models.Model):
    contact_name = CharField(max_length=70, null=False)
    city = CharField(max_length=30, null=False)
    state = CharField(max_length=30, null=True)
    address = CharField(max_length=70, null=False)

    class Meta:
        unique_together = (('contact_name', 'city', 'state', 'address'))

    def __repr__(self):
        return '<{}> {}'.format(self.__class__.__name__, self.__dict__)


class Transaction(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('in_progress', 'In Progress'),
    )

    PAYMENT_GATEWAY_CHOICES = (
        ('chapa', 'Chapa'),
        # Add more payment gateways as needed
    )

    tx_ref = models.CharField(max_length=100, unique=True)
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE, related_name='transactions')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    ebuss_amount = models.DecimalField(max_digits=10, decimal_places=2)
    supplier_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='ETB')
    payment_gateway = models.CharField(max_length=20, choices=PAYMENT_GATEWAY_CHOICES, default='chapa')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = DateTimeField(auto_now=True)
    verification_attempts = models.PositiveIntegerField(default=0)
    last_verification_time = models.DateTimeField(null=True, blank=True)
    payment_gateway_response = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tx_ref']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_gateway']),
        ]

    def save(self, *args, **kwargs):
        self.supplier_amount = self.total_amount * Decimal('0.8') 
        self.ebuss_amount = self.total_amount * Decimal('0.2')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Transaction {self.tx_ref} - {self.status}"

