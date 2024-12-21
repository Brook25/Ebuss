from django.test import TestCase
from models import (CartOrder, ProductOrder, Shipment, BillingInfo, ShipmentInfo, Payment)
# Create your tests here.
class TestOrder(TestCase):

    def setUp(self):

        billing_info_data_1 = {'contact_name': 'Taemr',
                    'city': 'Addis Ababa',
                    'state': None,
                    'email_address': 'taemrnegash@gmail.com',
                    'address': 'Karl square',
                    'phone_no': '0967101111',
                    'payment_method': 'CBEBirr'
                    }
        
        self.shipment_tracking_info = uuid.uuid4()
        
        shipment_info_data_1 = {k: v for k, v in billing_info_data.items()}.update({'tracking_info': self.shipment_tracking_info})
        
        payment_info_data_1 = {'user': self.test_user_2,
                        'amount': 2,
                        'status': 'in_progress'
                        }

        self.test_billing_info_1 = BillingInfo.objects.create(**billing_info_data_1)
        self.test_shipment_info_1 = ShipmentInfo.objects.create(**shipment_info_data_1)
        self.test_cart_order = CartOrder.objects.create(user=self.test_user_2,
                cart=self.test_cart_3,
                billing=self.test_billing_info_1,
                shipment=self.shipment_info_1)

        self.test_product_order = ProductOrder.objects.create(user=self.test_user_2,
                product=self.test_product_3,
                billing=self.test_billing_info_1,
                shipment_info=sipment_info_1)

        def test_billing_info(self):
            self.assertEqual(self.test_billing_info_1.contact_name='Taemr')
            self.assertEqual(self.test_billing_info.city='Addis Ababa')
            self.assertEqual(self.test_billing_info.state=None)
            self.assertEqual(self.test_billing_info.address='Karl square')
            self.assertEqual(self.test_billing_info.email_address='taemrnegash@gmail.com')
            self.assertEqual(self.test_billing_info.phone_no='0967101111')
            self.assertEqual(self.test_billing_info.payment_method='CBEBirr')
        
        def test_shipment_info(self):
            self.assertEqual(self.test_shipment_info_1.contact_name='Taemr')
            self.assertEqual(self.test_shipment_info.city='Addis Ababa')
            self.assertEqual(self.test_shipment_info.tracking_info=self.shipment_tracking_info)
            self.assertEqual(self.test_shipment_info.state=None)
            self.assertEqual(self.test_shipment_info.address='Karl square')
            self.assertEqual(self.test_shipment_info.email_address='taemrnegash@gmail.com')
            self.assertEqual(self.test_shipment_info.phone_no='0967101111')
            self.assertEqual(self.test_shipment_info.payment_method='CBEBirr')

        def test_cart_order(self):
            self.assetEqual(self.test_cart_order.user=self.test_user_2)
            self.assetEqual(self.test_cart_order.cart=self.test_cart_3)
            self.assetEqual(self.test_cart_order.billing=self.test_billing_info_1)
            self.assetEqual(self.test_cart_order.shipment=self.test_shipment_info)

        def test_product_order(self):
            self.assetEqual(self.test_product_order.user=self.test_user_2)
            self.assetEqual(self.test_product_order.cart=self.test_product_3)
            self.assetEqual(self.test_product_order.billing=self.test_billing_info_1)
            self.assetEqual(self.test_product_order.shipment=self.test_shipment_info)

