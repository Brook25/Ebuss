from django.test import TestCase
from datetime import datetime
from .models import (User, WishList, Notification)
from product.models import (Product, Category, SubCategory)
from order.models import (BillingInfo, ShipmentInfo, Payment)
from cart.models import Cart
from uuid import uuid
# Create your tests here.


class UserTest(TestCase):

    TEST_USER_1 = {
        'user_name': 'james_01',
        'email': 'james1@gmail.com',
        'first_name': 'James',
        'last_name': 'Del Toro',
        'country_code': 230
        'birth_date': '10-10-1995'
    }

    TEST_USER_2 = {
        'user_name': 'tommy_01',
        'email': 'tommy1@gmail.com',
        'first_name': 'Thomas',
        'last_name': 'Jefferson',
        'country_code': 232
        'birth_date': '18-10-1990'
    }

    test_product_1_features: {'brand': 'Aurora', 'screen': '14Mp'
            'ram': '16GB', 'storage': '64GB'}
    
    TEST_PRODUCT_1 = {
        'name': 'aurora2024',
        'description': 'Brand new phone. 14Mp camera, screen size 9.7". 16GB RAM, 64GB storage, Android 13',
        'price': 600,
        'quantity': 4,
        'tags': json.dumps(test_product_1_features)
        'tag_values': [test_product_1_features.values + ['aurora2024']]
    }


    def setup(self):
        """sets up user objects for the entire test."""
        self.test_user_1 = User.objects.create(**self.TEST_USER_1)
        self.test_user_2 = User.objects.create(**self.TEST_USER_2)
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
        self.test_billing_info = BillingInfo.objects.create(**billing_info_data)
        self.test_shipment_info = ShipmentInfo.objects.create(**payment_info_data)
        self.test_cart_1 = Cart.objects.create(name='mycart',
                customer=self.test_user_1, product=self.test_product_1, quantity=5)
        test_order = Order(user=self.test_order_2, cart=self.test_cart_1, billing=self.billing_info, shipment=self.shipment_info)
        

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
