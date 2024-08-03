from django.test import TestCase

# Create your tests here.

class TestProduct(TestCase):

    def setUp(self):
        super.setUp()
        test_product_3_data = {
            'name': 'vitamix',
            'description': 'Brand new blender. plastic jars, can be used for smoothies, self-cleaning, 400 watts',
            'price': 400,
            'quantity': 10,
            'sub_category': self.sub_category_3,
            'tags': json.dumps(test_product_3_features),
            'tag_values': [test_product_1_features.values + ['vitamix']]
        }

        test_product_4_data = {
            'name': 'Phillips refrigirator',
            'description': ' 4 shelves, fruit and vegetable section, LED lighting, Wi-Fi enabled, ventilation, dual cooling',
            'price': 1500,
            'quantity': 8,
            'sub_category': self.sub_category_4,
            'tags': json.dumps(test_product_1_features)
            'tag_values': [test_product_1_features.values + ['Phillipsrefrigirator']]
        }
        
        self.category_3 = Category.models.create(name='kitchen_appliances')
        self.category_4 = Category.models.create(name='cookware')
        self.category_5 = SubCategory.models.create(name='furniture')

        self.subcategory_3 = SubCategory.models.create(name='small_appliances', product=self.category_3)
        self.subcategory_4 = SubCategory.models.create(name='large_appliances', product=self.category_3)
        self.subcategory_5 = SubCategory.models.create(name='pots_and_pans', product=self.category_4)
        self.subcategory_6 = SubCategory.models.create(name='living_area', product=self.category_5)
        self.subcategory_7 = SubCategory.models.create(name='dining_area', product=self.category_5)
        
        self.test_product_3 = Product.models.create()
