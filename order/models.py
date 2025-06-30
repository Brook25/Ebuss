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
    amount = DecimalField(validators=[MinValueValidator(1)], max_digits=11, decimal_places=2, null=False)
    payment_gateway = CharField(choices=PAYMENT_GATEWAYS, default='chapa')
    trx_ref = CharField(unique=True)
    created_at = DateTimeField(auto_now=True)
    updated_at = DateTimeField(auto_now_add=True)
    status = CharField(max_length=30, choices=ORDER_STATUS_TYPES, default='pending')
    payment_status = CharField(choices=PAYMENT_STATUS_TYPES, default='pending')

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
    payment_gateway = models.CharField(max_length=20, choices=PAYMENT_GATEWAY_CHOICES)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
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
        self.supplier_amount = self.total_amount * 0.8 
        self.ebuss_amount = self.total_amount * 0.2
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Transaction {self.tx_ref} - {self.status}"

class SupplierPayment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('withdrawn', 'Withdrawn'),
    )

    supplier = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='supplier_earnings')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='supplier_earnings')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    withdrawn_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['supplier']),
            models.Index(fields=['transaction']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Earning for {self.supplier.username}: {self.amount}"

class SupplierWallet(models.Model):
    supplier = models.OneToOneField('user.User', on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_withdrawn = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    last_withdrawal = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['supplier']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.supplier.username}'s Wallet"

    def add_earning(self, amount):
        """Add earnings to the wallet"""
        self.balance += amount
        self.total_earned += amount
        self.save()

    def withdraw(self, amount):
        """Withdraw amount from wallet"""
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        
        self.balance -= amount
        self.total_withdrawn += amount
        self.last_withdrawal = timezone.now()
        self.save()

class SupplierWithdrawal(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )

    wallet = models.ForeignKey(SupplierWallet, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    bank_account = models.CharField(max_length=100)  # Or use a separate BankAccount model
    processed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['wallet']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Withdrawal of {self.amount} by {self.wallet.supplier.username}"

    def approve(self):
        """Approve the withdrawal request"""
        if self.status != 'pending':
            raise ValueError("Can only approve pending withdrawals")
        
        self.status = 'approved'
        self.processed_at = timezone.now()
        self.save()
        
        # Process the actual withdrawal
        self.wallet.withdraw(self.amount)
        
        # Update status to completed
        self.status = 'completed'
        self.save()

    def reject(self, notes=''):
        """Reject the withdrawal request"""
        if self.status != 'pending':
            raise ValueError("Can only reject pending withdrawals")
        
        self.status = 'rejected'
        self.notes = notes
        self.save()



