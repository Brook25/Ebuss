from django.db import models
from datetime import datetime
# Create your models here.



class Order(models.Model):
    user = ForeignKey('User', on_delete=models.CASCADE, related_name = 'orders')
    cart = ForeignKey('Cart', on_delete=models.DO_NOTHING)
    date = DateTimeField(default=datetime.now)
    billing_id = OneToOneField('BillingInfo', on_delete=models.CASCADE, related_name = 'order')
    shipment_id = OneToOneField('ShipmentInfo', on_delete=models.CASCADE, related_name = 'order')
    order_status = CharField(max_length=30, default='pending')
    
    def __repr__(self):
        return '<Order> {}'.format(self.__dict__)


class Shipment(models.Model):
    contact_name = CharField(max_length=70)
    city = CharField(max_length=30)
    state = CharField(max_length=30)
    email_address = EmailField()
    address = CharField(max_length=70)
    phone_no = CharField(max_length=70)


    class Meta:
        unique_together = ((contact_name, city, state, email_address, address, phone_no))

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
    payment_method = CharField(max_length=30)

    def get_or_create_billing_info(self, payment_data):
        return super.get_or_create_payment_data(payment_data)

class ShipmentInfo(Shipment):
    tracking_info = models.CharField(max_length=100)

    def get_or_create_shipment_info(self, payment_data):
        return super.get_or_create_payment_data(payment_data)

class Payment(models.Model):
    user = models.OneToMany('User', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(validators=[MinValidator(1)])
    date = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=('completed', 'reversed', 'declined'))
