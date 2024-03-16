from django.db import models


# Create your models here.

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
    category = ForeignKey('Category', on_delete=models.CASCADE, related_name='sub_categories')

class Review(models.Model):
    product = ForeignKey('Product', on_delete=models.DO_NOTHING, related_name='reviews')
    review = TextField(validators=[vulgarity_validator])
    rating = PositiveIntegerField()
    timestamp = DateTimeField(auto_now_add=True)

    def __repr__(self):
        return '<{}> {}'.format(self.__class__.__name__, self.__dict__)

class Metrics(models.Model):
    product = ForeignKey('Product', on_delete=models.DO_NOTHING, related_name='product_metrics')
    amount = PositiveIntegerField(default=1)
    customer = ForeingKey('User', on_delete=models.DO_NOTHING, related_name='customer_metrics')
    supplier = ForeingKey('User', on_delete=models.DO_NOTHING, related_name='supplier_metrics')
    purchase_date = DateField(auto_now_add=True)
    order = ForeignKey('Order', on_delete=models.CASCADE, related_name='order_metrics')
    total_price = PositiveIntegerField()


class Inventory(models.Model):
    product = ForeignKey('Product', on_delete=models.CASCADE, related_name='inventory_changes')
    date = DateField(auto_now_add=True)
    adjustment = IntegerField(required=True)
    type = CharField(Required=True)
    quantity_before = PositiveIntegerField()
    quantity_after = PositiveIntegerField()
    reason = CharField(max_length=255)
