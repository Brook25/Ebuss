from django.test import TestCase
from .cart import Cart
# Create your tests here.

def TestCart(TestCase):

    def setUp(self):
        test_cart_data = {
                'name': 'Mycart1',
                'customer': self.test_user_2,
                'product': self.test_product_3,
                'quantity': 4
                }

        self.test_cart_3 = Cart.objects.create(**test_cart_data)

    def test_cart(self):
        self.assertEqual(self.test_cart_3.name='Mycart1')
        self.assertEqual(self.test_cart_3.customer=self.test_user_2)
        self.assertEqual(self.test_cart_3.product=self.test_product_3)
        self.assertEqual(self.test_cart_3.quantity=4)
