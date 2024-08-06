from django.test import TestCase
import json
# Create your tests here.

class TestProduct(TestCase):

    def setUp(self):
        super.setUp()
        
        test_user_3_data = {
                        'first_name': 'Veronica',
                        'last_name': 'Thomas',
                        'email': 'viccytom@gmail.com',
                        'password': 'viccytom27!',
                        'birth_date': '10-10-1991',
                        }
        
        test_user_4_data = {
                        'first_name': 'Peter',
                        'last_name': 'Parker',
                        'email': 'peterpark@gmail.com',
                        'password': 'peterboy27!',
                        'birth_date': '10-10-1993',
                        }
        
        test_user_5_data = {
                        'first_name': 'Helen',
                        'last_name': 'Yonas',
                        'email': 'helenyoni@gmail.com',
                        'password': 'helenyoni27!',
                        'birth_date': '10-9-1995',
                        }
        
        test_user_6_data = {
                        'first_name': 'Yonas',
                        'last_name': 'Abebe',
                        'email': 'yonnyabe@gmail.com',
                        'password': 'yonyboy27!',
                        'birth_date': '01-10-1994',
                        }
        
        
        test_product_3_features: {'brand': 'vitamix', 'power': '400 watts',
                'blade': 'steel'}
        
        test_product_4_features: {'brand': 'phillips',
                'no of shelves': '4 shelves', 'dual-cooling': True,
                'ventillation': True, 'wi-fi': True}
        
        test_product_5_features: {'brand': 'all-clad', 'model': 'd3',
                'stainless-steel': True, 'thickness': '12 inches'}
        
        test_product_7_features: {'brand': 'EW2', 'length': '193cm',
                'width': '90cm', 'thickness': '2cm', 'extendable': True}
        
        test_product_6_features: {'brand': 'EW2', 'length': '193cm', 'table shape': 'oval', 'thickness': '2cm', 'type': 'modern'}
        
        test_product_3_data = {
            'name': 'vitamix',
            'description': 'Brand new blender. plastic jars, can be used for smoothies, self-cleaning, 400 watts',
            'price': 400,
            'quantity': 10,
            'supplier': self.test_user_3,
            'sub_category': self.sub_category_3,
            'tags': json.dumps(test_product_3_features),
            'tag_values': [test_product_1_features.values + ['vitamix']]
        }

        test_product_4_data = {
            'name': 'phillips refrigirator',
            'description': '4 shelves, fruit and vegetable section, LED lighting, Wi-Fi enabled, ventilation, dual cooling',
            'price': 3000,
            'quantity': 8,
            'supplier': self.test_user_4,
            'sub_category': self.sub_category_4,
            'tags': json.dumps(test_product_1_features)
            'tag_values': [test_product_1_features.values + ['phillips refrigirator']]
        }

        test_product_5_data = {
            'name': 'all-clad',
            'description': 'd3 stainless steel, 12 inch fry pan, nonstick, oven safe',
            'price': 1500,
            'quantity': 20,
            'supplier': self.test_user_5
            'sub_category': self.sub_category_5,
            'tags': json.dumps(test_product_1_features)
            'tag_values': [test_product_1_features.values + ['all-clad']]
        }

        test_product_7_data = {
            'name': 'EW2',
            'description': 'dining area set, rectangular table, 193cmX90cm, 2cm thickness, expandable',
            'price': 700,
            'quantity': 10,
            'sub_category': self.sub_category_7,
            'supplier': self.test_user_6,
            'tags': json.dumps(test_product_7_features)
            'tag_values': [test_product_1_features.values + ['all-clad']]
        }

        test_product_6_data = {
            'name': 'EW2',
            'description': 'living area set, oval table, 150 cm length, 2cm thickness, glass top, sleek lines, minimalist design, light grey',
            'price': 5000,
            'quantity': 8,
            'supplier': self.test_user_6,
            'sub_category': self.sub_category_6,
            'tags': json.dumps(test_product_6_features)
            'tag_values': [test_product_1_features.values + ['all-clad']]
        }
        
        test_review_text = 'Such a great product. Do reccommend it.'
        test_rating = 5
        
        self.test_user_3 = User.objects.create(**test_user_3_data)
        self.test_user_4 = User.objects.create(**test_user_4_data)
        self.test_user_5 = User.objects.create(**test_user_5_data)
        self.test_user_6 = User.objects.create(**test_user_6_data)
        self.test_review_1 = Review.objects.create(user=self.test_user_2, product=self.test_product_3,
                review=test_review_text, rating=test_rating)        
        self.category_3 = Category.models.create(name='kitchen_appliances')
        self.category_4 = Category.models.create(name='cookware')
        self.category_5 = Category.models.create(name='furniture')

        self.subcategory_3 = SubCategory.models.create(name='small_appliances', product=self.category_3)
        self.subcategory_4 = SubCategory.models.create(name='large_appliances', product=self.category_3)
        self.subcategory_5 = SubCategory.models.create(name='pots_and_pans', product=self.category_4)
        self.subcategory_6 = SubCategory.models.create(name='living_area', product=self.category_5)
        self.subcategory_7 = SubCategory.models.create(name='dining_area', product=self.category_5)
        
        self.test_product_3 = Product.models.create(**test_product_3)
        self.test_product_4 = Product.models.create(**test_product_4)
        self.test_product_5 = Product.models.create(**test_product_5)
        self.test_product_6 = Product.models.create(**test_product_6)
        self.test_product_7 = Product.models.create(**test_product_7)
        


    def test_category_3(self):
        self.assertEqual(self.category_3.name='kitchen_appliances')
    
    def test_category_4(self):
        self.assertEqual(self.category_4.name='cookware')

    def test_category_5(self):
        self.assertEqual(self.category_5.name='furniture')

    def test_subcategory_3(self):
        self.assertEqual(self.subcategory_3.name='small_appliances')
        self.assertEqual(self.subcategory_3.product=self.category_3)
    
    def test_subcategory_4(self):
        self.assertEqual(self.subcategory_4.name='large_appliances')
        self.assertEqual(self.subcategory_4.product=self.category_3)

    def test_subcategory_5(self):
        self.assertEqual(self.subcategory_5.name='pots_and_pans')
        self.assertEqual(self.subcategory_5.product=self.category_4)

    def test_subcategory_6(self):
        self.assertEqual(self.category_6.name='living_area')
        self.assertEqual(self.category_6.product=self.category_5)

    def test_subcategory_7(self):
        self.assertEqual(self.category_7.name='dining_area')
        self.assertEqual(self.category_7.product=self.category_5)

    def test_product_3(self):
        self.assertEqual(self.test_product_3.name='vitamix')
        self.assertEqual(self.test_product_3.description='Brand new blender. plastic jars, can be used for smoothies, self-cleaning, 400 watts')
        self.assertEqual(self.test_product_3.price=400)
        self.assertEqual(self.test_product_3.quantity=10)
        self.assertEqual(self.test_product_3.supplier=self.test_user_3)
        self.assertEqual(self.test_product_3.subcategory=self.sub_category_3)
        self.assertEqual(json.loads(self.test_product_3.tags)=self.test_product_3_features)
        self.assertEqual(json.loads(self.test_product_3.tags).values=self.test_product_3_features.values)
    
    def test_product_4(self):
        self.assertEqual(self.test_product_4.name='phillips refrigirator')
        self.assertEqual(self.test_product_4.description='4 shelves, fruit and vegetable section, LED lighting, Wi-Fi enabled, ventilation, dual cooling')
        self.assertEqual(self.test_product_4.price=3000)
        self.assertEqual(self.test_product_4.quantity=8)
        self.assertEqual(self.test_product_4.supplier=self.test_user_4)
        self.assertEqual(self.test_product_4.subcategory=self.sub_category_4)
        self.assertEqual(json.loads(self.test_product_4.tags)=self.test_product_4_features)
        self.assertEqual(json.loads(self.test_product_4.tags).values=self.test_product_4_features.values)
    
    def test_product_5(self):
        self.assertEqual(self.test_product_5.name='all-clad')
        self.assertEqual(self.test_product_5.description='d3 stainless steel, 12 inch fry pan, nonstick, oven safe')
        self.assertEqual(self.test_product_5.price=1500)
        self.assertEqual(self.test_product_5.quantity=20)
        self.assertEqual(self.test_product_5.supplier=self.test_user_5)
        self.assertEqual(self.test_product_5.subcategory=self.sub_category_5)
        self.assertEqual(json.loads(self.test_product_5.tags)=self.test_product_5_features)
        self.assertEqual(json.loads(self.test_product_5.tags).values=self.test_product_5_features.values)
    
    def test_product_6(self):
        self.assertEqual(self.test_product_6.name='EW2')
        self.assertEqual(self.test_product_6.description='living area set, oval table, 150 cm length, 2cm thickness, glass top, sleek lines, minimalist design, light grey')
        self.assertEqual(self.test_product_6.price=1500)
        self.assertEqual(self.test_product_6.quantity=8)
        self.assertEqual(self.test_product_6.supplier=self.test_user_6)
        self.assertEqual(self.test_product_6.subcategory=self.sub_category_6)
        self.assertEqual(json.loads(self.test_product_6.tags)=self.test_product_6_features)
        self.assertEqual(json.loads(self.test_product_6.tags).values=self.test_product_6_features.values)
    
    def test_product_7(self):
        self.assertEqual(self.test_product_7.name='EW2')
        self.assertEqual(self.test_product_7.description='dining area set, rectangular table, 193cmX90cm, 2cm thickness, expandable')
        self.assertEqual(self.test_product_7.price=400)
        self.assertEqual(self.test_product_7.quantity=10)
        self.assertEqual(self.test_product_7.supplier=self.test_user_6)
        self.assertEqual(self.test_product_7.subcategory=self.sub_category_7)
        self.assertEqual(json.loads(self.test_product_7.tags)=self.test_product_7_features)
        self.assertEqual(json.loads(self.test_product_7.tags).values=self.test_product_7_features.values)

    def test_review_rating_notnull(self):
        self.assertEqual(self.test_review_1.user=self.test_user_2)
        self.assertEqual(self.test_review_1.product=self.test_product_3)
        self.assertEqual(self.test_review_1.review='Such a great product. Do reccommend it.')
        self.assertEqual(self.test_review_1.rating=5)
