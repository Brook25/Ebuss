from django.core.validators import (MinValueValidator)
from django.db.models import (ForeignKey, DateField, DecimalField, PositiveIntegerField,
                        IntegerField, CharField)
from django.db import models
from decimal import Decimal

class Metrics(models.Model):
    product = ForeignKey('product.Product', on_delete=models.CASCADE, related_name='product_metrics')
    quantity = PositiveIntegerField(default=1)
    customer = ForeignKey('user.User', on_delete=models.CASCADE, related_name='customer_metrics')
    supplier = ForeignKey('user.User', on_delete=models.CASCADE, related_name='supplier_metrics')
    purchase_date = DateField(auto_now_add=True)
    total_price = PositiveIntegerField(null=False, blank=False)


class Inventory(models.Model):
    product = ForeignKey('product.Product', on_delete=models.CASCADE, related_name='inventory_changes')
    created_at = DateField(auto_now_add=True)
    adjustment = IntegerField(null=False, blank=False)
    quantity_before = PositiveIntegerField(null=False, blank=False)
    quantity_after = PositiveIntegerField(null=False, blank=False)
    reason = CharField(max_length=255, null=True)


class SupplierWallet(models.Model):
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('suspended', 'Suspended'),
    )
    
    supplier = models.OneToOneField('user.User', on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    status = CharField(choices=STATUS_CHOICES, null=False, default='active')

    class Meta:
        indexes = [
            models.Index(fields=['supplier']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.supplier.username}'s Wallet"


class SupplierWithdrawal(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )

    withdrawal_account = models.ForeignKey('WithdrawalAcct', on_delete=models.DO_NOTHING, related_name='withdrawals')
    status = models.CharField(choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    reference = models.CharField(max_length=100)
    processed_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['wallet']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Withdrawal of {self.amount} by {self.wallet.supplier.username}"


class WithdrawalAcct(models.Model):
    ACCT_NAMES = (
            ('telebirr', 'Telebirr'),
            ('cbe', 'CBE'),
            ('awash', 'Awash Birr'),
    )

    wallet = models.ForeingKey(SupplierWallet, on_delete=models.CASCADE, unique=False, related_name='withdrawal_accounts')
    name = models.CharField(choices=ACCT_NAMES)
    holder_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=100)

    def __str__(self):
        return f'<withdrawal account>: {self.__dict__}'
