from django.core.validators import (MinValueValidator)
from django.db.models import (ForeignKey, DateField, DecimalField, PositiveIntegerField,
                        IntegerField, CharField)
from django.db import models
# Create your models here.

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
    
    user = ForeignKey('user.User', on_delet=models.CASCADE, related_name='supplier_obj')
    balance = DecimalField(max_digits=11, decimal_places=2, validators=[MinValueValidator(0)])
    status = CharField(choices=STATUS_CHOICES, null=False)
    last_withdrawal_data = DateField()