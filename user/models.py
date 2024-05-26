from django.db import models
from Product.models import Product
# Create your models here.

PRIORITY_CHOICES = (
        ('HIGH', 'High'),
        ('MEDIUM', 'MEDIUM'),
        ('LOW', 'Low'),
        )


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
    wishlist = ForeignKey('Wishlist', related_name='wishlist_for')
    recommendations = ManyToManyField('Product', related_name='recommended_to') 

    REQUIRED_FIELDS = ['first_name', 'last_name', 'birth_date', 'phone_no']

    def __repr__(self):
        return '<User> firstname: {}, lastname: {}, username: {}, email: {}'.format(self.first_name, self.last_name, self.username, self.email)


class History(models.Model):
    customer = ForeignKey('User', on_delete=models.CASCADE, related_name='purchase_history')
    supplier = ForeignKey('User', on_delete=models.DO_NOTHING, related_name='purchased_items_history')
    product_name = CharField(max_length=70)
    billing_address = CharField(max_length=70)
    payment_mmethod = CharField(max_length=20)
    shippment_address = CharField(max_length=70)

class Wishlist(models.Model):
    created_at = DateTimeField(auto_add_now=True)
    products = ManyToManyField('Product', related_name='wishlists_in')
    priority = CharField(choices=PRIORITY_CHOICES, default='LOW')


class Notification(models.Model):
    user = ForeignKey('User', on_delete=models.CASCADE, related_name='notifications')
    created_at = DateTimeField(auto_add_now=True)
    note = TextField()
    uri = URLField(max_length=200)

class Metrics(models.Model):
    product = ForeignKey('Product', on_delete=models.DO_NOTHING, related_name='product_metrics')
    quantity = PositiveIntegerField(default=1)
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
