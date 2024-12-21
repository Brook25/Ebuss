from django.db import models
from shared.validators import check_vulgarity
from django.db.models import (
        CharField, DateTimeField, ForeignKey,
        PositiveIntegerField, ManyToManyField
        )


class Cart(models.Model):
    name = CharField(max_length=40, validators=[check_vulgarity], null=False, blank=False)
    customer = ForeignKey('user.User', on_delete=models.CASCADE, related_name='carts')
    timestamp = DateTimeField(auto_now=True)
    product = ManyToManyField('product.Product', related_name='carts_in')
    quantity = PositiveIntegerField(default=1)

    def __repr__(self):
        return '<Cart> {}'.format(self.__dict__)
