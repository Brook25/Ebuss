from django.db import models
from shared.validators import check_vulgarity
from django.db.models import (
        CharField, DateTimeField, ForeignKey,
        PositiveIntegerField, Q
        )

CART_STATUS = (('active', 'Active'),
                  ('inactive', 'inactive'))


class Cart(models.Model):
    user = ForeignKey('user.User', on_delete=models.CASCADE, related_name='carts')
    created_at = DateTimeField(auto_now=True)
    status = CharField(choices=CART_STATUS, null=False, default='active')


    class Meta:
        constraints = [
                models.UniqueConstraint(fields=['user'],
                    condition=Q(status='active'),
                    name='unique_active_cart_for_user')
                ]

    def __repr__(self):
        return '<Cart> {}'.format(self.__dict__)


class CartData(models.Model):
    cart = ForeignKey('Cart', related_name='cart_data_for', on_delete=models.CASCADE)
    product = ForeignKey('product.Product', related_name='product_data_for', on_delete=models.DO_NOTHING)
    quantity = PositiveIntegerField(default=1)
    created_at = DateTimeField(auto_now=True)

    def __repr__(self):
        return '<CartData> {}'.format(self.__dict__)

    class Meta:
        unique_together = ('cart', 'product')
