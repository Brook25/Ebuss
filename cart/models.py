from django.db import models


class Cart(models.Model):
    name = CharField(max_length=40, validators=[vulgarity_validator])
    customer = ForeignKey('User', on_delete=models.CASCADE, related_name='carts')
    timestamp = DateTimeField(auto_now=True)
    product = ManyToManyField('Product')
    quantity = PositiveIntegerField()

    def __repr__(self):
        return '<Cart> {}'.format(self.__dict__)
