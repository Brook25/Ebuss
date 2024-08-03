from django.test import TestCase
from datetime import datetime
from .models import (User, WishList, Notification)
from product.models import (Product, Category, SubCategory)
from order.models import (BillingInfo, ShipmentInfo, Payment)
from cart.models import Cart
from uuid import uuid
# Create your tests here.


class UserTest(TestCase):


    def setup(self):
        """sets up user objects for the entire test."""
        test_user_1_data = {
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'email': 'johndoe@gmail.com',
                        'password': 'johnnyboy27!',
                        'birth_date': '10-10-1995',
                        }

        test_user_2_data = {
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'email': 'johndoe@gmail.com',
                        'password': 'johnnyboy27!',
                        'birth_date': '10-10-1995',
                }
        self.test_user_1 = User.objects.create(**test_user_1_data)
        self.test_user_2 = User.objects.create(**test_user_2_data)
        self.category_1 = Category.models.create(name='electronics')
        self.category_2 = Category.models.create(name='cloth')
        self.sub_category_1 = SubCategory.models.create(name='phone', category=self.category_1)
        self.sub_category_2 = SubCategory.models.create(name='women_cloths', category=self.category_2)
        test_product_1_features: {'brand': 'Aurora', 'screen': '14Mp'
                'ram': '16GB', 'storage': '64GB'}
        
        test_product_1_data = {
            'name': 'aurora2024',
            'description': 'Brand new phone. 14Mp camera, screen size 9.7". 16GB RAM, 64GB storage, Android 13',
            'price': 600,
            'quantity': 4,
            'sub_category': self.sub_category_1,
            'tags': json.dumps(test_product_1_features),
            'tag_values': [test_product_1_features.values + ['aurora2024']]
        }

        test_product_2_data = {
            'name': 'circle_t_shirt',
            'description': 'Brand new phone. 14Mp camera, screen size 9.7". 16GB RAM, 64GB storage, Android 13',
            'price': 600,
            'quantity': 4,
            'sub_category': self.sub_category_2
            'tags': json.dumps(test_product_1_features)
            'tag_values': [test_product_1_features.values + ['aurora2024']]
        }
        self.test_product_1 = Product.objects.create(**test_product_1_data)
        self.test_product_2 = Product.objects.create(**test_product_2_data) 
        billing_info_data = {'contact_name': 'John',
                    'city': 'Addis Ababa',
                    'state': None,
                    'email_address': 'johnnyboy24@gmail.com',
                    'address': 'Mexico square',
                    'phone_no': '0967101001',
                    'payment_method': 'TeleBirr'
                    }
        shipment_info_data = {k: v for k, v in billing_info_data.items()}.update({'tracking_info': uuid.uuid4()})
        payment_info_data = {'user': self.test_user_1,
                        'amount': 2,
                        'status': 'in_progress'
                        }
        self.test_billing = BillingInfo.objects.create(**billing_info_data)
        self.test_shipment = ShipmentInfo.objects.create(**payment_info_data)
        self.test_cart_1 = Cart.objects.create(name='mycart',
                customer=self.test_user_1, product=self.test_product_1, quantity=5)
        self.test_order = Order(user=self.test_user_2, cart=self.test_cart_1, billing=self.billing_info, shipment=self.shipment_info)
        

    def test_create_user_1(self):
        """This test tests user creation and field validation."""
        value = (User.objects.filter(user=self.test_user_1) == self.test_user_1)        self.assert_True(value)

    def test_email_user_1(self):
        self.assert_equal(self.test_user_1.first_name, 'Thomas')

    def test_country_code_user_1(self):
        self.assert_equal(self.country_code, 230)
    
    def test_birth_date_user_1(self):
        format_string = '%d-%m-%Y'
        creation_date = datetime.strptime('18-10-1995', format_string)
        self.assert_equal(self.birth_date, creation_date)
   
   def test_wish_list(self):
        self.TEST_PRODUCT_2['subcategory'] = self.sub_category_2
        test_product_2 = Product.objects.create(**self.TEST_PRODUCT_2)
        wish_list_1_data = {'created_by': self.test_user_1,
                'product': self.test_product_1}
        test_wishlist_1 = WishList.objects.create(**wish_list_1_data)
        assertEqual(test_wishlist_1.created_by, self.test_user_1)
        assertEqual(test_wishlist_1.product, self.test_product_1)
        assertEqual(test_wishlist_1.priority, 'LOW')

    def test_notification(self):
        test_not_data = {'user': self.test_user_1,
                        'note': 'Your order has been succefully registered.',
                        'type': 'order_status',
                        'uri': 'https://127.0.0.1/orders'}
        test_not_1 = Notification.models.create(**test_not_data)
        assertEqual(test_not_1.user, self.test_user_1)
        assertEqual(test_not_1.note, 'Your order has been succefully registered.')
        assertEqual(test_not_1.type, 'order_status')
        assertEqual(test_not_1.uri, 'https://127.0.0.1/orders')

    def test_history_with_cart(self):
        
        test_history = History.objects.create(cart=test_cart_1, billing_address=self.billing_address, shipment_info=self.shipment_info, payment_info=self.payment_info)
        assertEqual(test_history.cart=test_cart_1)
        assertEqual(test_history.billing_address.contact_name='John')
        assertEqual(test_history.billing_address.city='Addis Ababa')
        assertEqual(test_history.billing_address.address='Mexico Square')
        assertEqual(test_history.billing_address.phone_no='0967101001')
        assertEqual(test_history.billing_address.payment='TeleBirr')

    def test_history_with_product(self):
        
        test_history = History.object.create(product=self.test_product_1, billing_address=self.billing_address, shipment_info=self.shipment_info, payment_info=self.payment_info)
        assertEqual(test_history.cart=self.test_product_1)
        assertEqual(test_history.billing_address.contact_name='John')
        assertEqual(test_history.billing_address.city='Addis Ababa')
        assertEqual(test_history.billing_address.address='Mexico Square')
        assertEqual(test_history.billing_address.phone_no='0967101001')
        assertEqual(test_history.billing_address.payment='TeleBirr')

    def test_metrics(self):

        test_matrics = Matrics.objects.create(product=self.test_product_1,
                quantity=2, customer=self.test_user_2, supplier=self.test_user_1, order=self.test_order, total_price=self.test_product_1.price * 2)
        assertEqual(test_matrics.product.name=self.test_product_1.name)
        assertEqual(test_matrics.quantity=2)
        assertEqual(test_matrics.customer.name=self.test_user_2.name)
        assertEqual(test_matrics.supplier.name=self.test_user_1.name)
        assertEqual(test_matrics.order.customer=self.test_user_2.name)
        assertEqual(test_matrics.total_price=self.test_product_1.price * 2)

    def test_inventory(self):
        test_inventory_data = { 'product': self.test_product_1,
                        'adjustment': 5,
                        'quantity_before': self.test_prodcut_1.quantity,
                        'quantity_after': self.test_product_1.quantity + 5,
                        'reason': 'shortage in stock'
                        }
        quantity_before = self.test_product.quantity
        self.test_product_1.quantity += 5
        self.test_product_1.save()

        test_inventory_change = Inventroy.objects.create(**test_inventory_data)
        self.assertEqual(test_inventory_change.product=self.test_product)
        self.assertEqual(test_inventory_change.adjustment=5)
        self.assertEqual(test_inventory_change.quantity_before=quantity_before)
        self.assertEqual(test_inventory_change.quantity_after=self.test_product_1)
        self.assertEqual(test_inventory_change.reason='shortage in stock')

    def tearDown(self):
        self.test_product_1.delete()
        self.test_product_2.delete()
        self.test_user_1.delete()
        self.test_user_2.delete()
        self.test_category_1.delete()
        self.test_category_2.delete()
        self.test_subcategory_2.delete()
        self.test_cart_1.delete()
        self.billing_info.delete()
        self.shipment_info.delete()
        self.test_order.delete()
