from django.db import models

# Create your models here.

class Order(models.Model):
    customer = ForeignKey('User', on_delete=models.CASCADE, related_name = 'orders')
    product = ForeignKey('Product', on_delete=models.DO_NOTHING)
    date = DateTimeField(default=datetime.now)
    quantity = PositiveIntegerField()
    billing_id = OneToOneField('BillingInfo', on_delete=models.CASCADE, related_name = 'order')
    shipment_id = OneToOneField('ShipmentInfo', on_delete=models.CASCADE, related_name = 'order')
    order_status = CharField(max_length=30, default='Pending')
    
    def __repr__(self):
        return '<Order> {}'.format(self.__dict__)


class Cart(models.Model):
    name = CharField(max_length=40, validators=[vulgarity_validator])
    customer = ForeignKey('User', on_delete=models.CASCADE, related_name='carts')
    timestamp = DateTimeField(auto_now=True)
    products = ManyToManyField('Product')

    def __repr__(self):
        return '<Cart> {}'.format(self.__dict__)


class PaymentAndShipment(models.Model):
    contact_name = CharField(max_length=70)
    city = CharField(max_length=30)
    state = CharField(max_length=30)
    email_address = EmailField()
    address = CharField(max_length=70)
    phone_no = CharField(max_length=70)

    def __repr__(self):
        return '<{}> {}'.format(self.__class__.__name__, self.__dict__)

class BillingInfo(PaymentAndShipment):
    payment_method = CharField(max_length=30)


class ShipmentInfo(PaymentAndShipment):
    tracking_info = models.CharField(max_length=100)
