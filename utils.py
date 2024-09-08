import json
from user.models import (User, Wishlist) 
from product.models import (Product, Category, SubCategory, Review)
from order.models import (CartOrder, SingleProductOrder, ShipmentInfo, BillingInfo)
from cart.models import Cart
from post.models import (Post, Comment, Reply)
import uuid


class SetupObjects:
    
    def create_test_objects(self):

        test_user_1_data = {
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'username': 'johnnydoe1',
                        'email': 'johndoe@gmail.com',
                        'password': 'johnnyboy27!',
                        'birth_date': '1995-10-10',
                        }

        test_user_2_data = {
                        'first_name': 'Emily',
                        'last_name': 'James',
                        'username': 'emilyjim1',
                        'email': 'emilyjames@gmail.com',
                        'password': 'emilyjames27!',
                        'birth_date': '1995-10-10',
                }
        
        test_user_1 = User.objects.create(**test_user_1_data)
        test_user_2 = User.objects.create(**test_user_2_data)
        
        test_product_1_features = { 'brand': 'Aurora', 'screen': '14Mp',
                'ram': '64GB', 'os': 'android13', 'storage': '64GB' }
        
        test_product_2_features = {'brand': 'H&M', 'fiber': 'cotton',
            'style': 'casual', 'neck': 'round'}
        
        category_1 = Category.objects.create(name='electronics')
        category_2 = Category.objects.create(name='cloth')
        sub_category_1 = SubCategory.objects.create(name='phone', category=category_1)
        sub_category_2 = SubCategory.objects.create(name='women_cloths', category=category_2)
        
        test_product_1_data = {
            'name': 'aurora2024',
            'supplier': test_user_1,
            'description': 'Brand new phone. 14Mp camera, screen size 9.7". 16GB RAM, 64GB storage, Android 13',
            'price': 600,
            'quantity': 4,
            'sub_category': sub_category_1,
            'tags': json.dumps(test_product_1_features),
            'tag_values': [list(test_product_1_features.values()) + ['aurora2024']]
        }

        test_product_2_data = {
            'name': 'round_neck_t-shirt',
            'supplier': test_user_1,
            'description': 'H&M circle T-shirt soft, cotton made casual',
            'price': 200,
            'quantity': 8,
            'sub_category': sub_category_2,
            'tags': json.dumps(test_product_2_features),
            'tag_values': [list(test_product_2_features.values()) + ['H&M circle_t-shirt']]
        }

        test_product_1 = Product.objects.create(**test_product_1_data)
        
        test_product_2 = Product.objects.create(**test_product_2_data) 
        billing_info_data = {'contact_name': 'John',
                    'city': 'Addis Ababa',
                    'state': None,
                    'email_address': 'johnnyboy24@gmail.com',
                    'address': 'Mexico square',
                    'phone_no': '0967101001',
                    'payment_method': 'TeleBirr'
                    }
        shipment_info_data = {k: v for k, v in billing_info_data.items()}
        shipment_info_data.pop('payment_method')
        shipment_info_data['tracking_info'] = uuid.uuid4()
        print(shipment_info_data)
        payment_info_data = {'user': test_user_2,
                        'amount': 2,
                        'status': 'in_progress'
                        }
        test_billing = BillingInfo.objects.create(**billing_info_data)
        test_shipment = ShipmentInfo.objects.create(**shipment_info_data)
        test_cart_1 = Cart.objects.create(name='mycart', customer=test_user_2, quantity=5)
        test_cart_1.product.set([test_product_1])
        test_cartorder = CartOrder.objects.create(user=test_user_2, cart=test_cart_1, billing=test_billing, shipment=test_shipment)
        test_singleproduct_order = SingleProductOrder.objects.create(user=test_user_2, product=test_product_1, billing=test_billing, shipment=test_shipment)
        
        wish_list_1_data = { 'created_by': test_user_2 }
        test_wishlist_1 = Wishlist.objects.create(**wish_list_1_data)
        test_wishlist_1.product.add(test_product_2)
        
        test_user_3_data = {
                        'first_name': 'Veronica',
                        'last_name': 'Thomas',
                        'username': 'vertom1',
                        'email': 'viccytom@gmail.com',
                        'password': 'viccytom27!',
                        'birth_date': '1991-10-10',
                        }
        
        test_user_4_data = {
                        'first_name': 'Peter',
                        'last_name': 'Parker',
                        'username': 'peterpark1',
                        'email': 'peterpark@gmail.com',
                        'password': 'peterboy27!',
                        'birth_date': '1993-10-10',
                        }
        
        test_user_5_data = {
                        'first_name': 'Helen',
                        'last_name': 'Yonas',
                        'username': 'helenyon1',
                        'email': 'helenyoni@gmail.com',
                        'password': 'helenyoni27!',
                        'birth_date': '1995-10-10',
                        }
        
        test_user_6_data = {
                        'first_name': 'Yonas',
                        'last_name': 'Abebe',
                        'username': 'yonyabe1',
                        'email': 'yonnyabe@gmail.com',
                        'password': 'yonyboy27!',
                        'birth_date': '1994-10-10',
                        }
        
        test_user_3 = User.objects.create(**test_user_3_data)
        test_user_4 = User.objects.create(**test_user_4_data)
        test_user_5 = User.objects.create(**test_user_5_data)
        test_user_6 = User.objects.create(**test_user_6_data)
        
        category_3 = Category.objects.create(name='kitchen_appliances')
        category_4 = Category.objects.create(name='cookware')
        category_5 = Category.objects.create(name='furniture')

        subcategory_3 = SubCategory.objects.create(name='small_appliances', category=category_3)
        subcategory_4 = SubCategory.objects.create(name='large_appliances', category=category_3)
        subcategory_5 = SubCategory.objects.create(name='pots_and_pans', category=category_4)
        subcategory_6 = SubCategory.objects.create(name='living_area', category=category_5)
        subcategory_7 = SubCategory.objects.create(name='dining_area', category=category_5)
        
        test_product_3_features = {'brand': 'vitamix', 'power': '400 watts',
                'blade': 'steel'}
        
        test_product_4_features = {'brand': 'phillips',
                'no of shelves': '4 shelves', 'dual-cooling': True,
                'ventillation': True, 'wi-fi': True}
        
        test_product_5_features = {'brand': 'all-clad', 'model': 'd3',
                'stainless-steel': True, 'thickness': '12 inches'}
        
        test_product_7_features = {'brand': 'EW2', 'length': '193cm',
                'width': '90cm', 'thickness': '2cm', 'extendable': True}
        
        test_product_6_features = {'brand': 'EW2', 'length': '193cm', 'table shape': 'oval', 'thickness': '2cm', 'type': 'modern'}
        
        test_product_3_data = {
            'name': 'vitamix',
            'description': 'Brand new blender. plastic jars, can be used for smoothies, self-cleaning, 400 watts',
            'price': 400,
            'quantity': 10,
            'supplier': test_user_3,
            'sub_category': subcategory_3,
            'tags': json.dumps(test_product_3_features),
            'tag_values': [list(test_product_3_features.values()) + ['vitamix']]
        }

        test_product_4_data = {
            'name': 'phillips refrigirator',
            'description': '4 shelves, fruit and vegetable section, LED lighting, Wi-Fi enabled, ventilation, dual cooling',
            'price': 3000,
            'quantity': 8,
            'supplier': test_user_4,
            'sub_category': subcategory_4,
            'tags': json.dumps(test_product_4_features),
            'tag_values': [list(test_product_4_features.values()) + ['phillips refrigirator']]
        }

        test_product_5_data = {
            'name': 'all-clad',
            'description': 'd3 stainless steel, 12 inch fry pan, nonstick, oven safe',
            'price': 1500,
            'quantity': 20,
            'supplier': test_user_5,
            'sub_category': subcategory_5,
            'tags': json.dumps(test_product_5_features),
            'tag_values': [list(test_product_5_features.values()) + ['all-clad']]
        }

        test_product_7_data = {
            'name': 'EW2',
            'description': 'dining area set, rectangular table, 193cmX90cm, 2cm thickness, expandable',
            'price': 700,
            'quantity': 10,
            'sub_category': subcategory_7,
            'supplier': test_user_6,
            'tags': json.dumps(test_product_7_features),
            'tag_values': [list(test_product_7_features.values()) + ['all-clad']]
        }

        test_product_6_data = {
            'name': 'EW2',
            'description': 'living area set, oval table, 150 cm length, 2cm thickness, glass top, sleek lines, minimalist design, light grey',
            'price': 5000,
            'quantity': 8,
            'supplier': test_user_6,
            'sub_category': subcategory_6,
            'tags': json.dumps(test_product_6_features),
            'tag_values': [list(test_product_1_features.values()) + ['all-clad']]
        }
        
        test_product_3 = Product.objects.create(**test_product_3_data)
        test_product_4 = Product.objects.create(**test_product_4_data)
        test_product_5 = Product.objects.create(**test_product_5_data)
        test_product_6 = Product.objects.create(**test_product_6_data)
        test_product_7 = Product.objects.create(**test_product_7_data)
        test_review_text = 'Such a great product. Do reccommend it.'
        test_rating = 5
        
        test_review_1 = Review.objects.create(user=test_user_2, product=test_product_3,
        review=test_review_text, rating=test_rating)        
        
        
        test_cart_data = {
                'name': 'Mycart1',
                'customer': test_user_2,
                'product': test_product_3,
                'quantity': 4
                }
        test_user_3_data = {
                        'first_name': 'James',
                        'last_name': 'Trim',
                        'username': 'jimmytim1',
                        'email': 'jamestrim@gmail.com',
                        'password': 'jamestrim27!',
                        'birth_date': '1990-10-10',
                }
        
        test_user_4_data = {
                        'first_name': 'Helena',
                        'last_name': 'Peter',
                        'username': 'helenpet1',
                        'email': 'helenapet@gmail.com',
                        'password': 'helena27!',
                        'birth_date': '1993-10-10',
                }
        
        post_text = 'Check out this new product.'
        comment_text = 'Its really great.'
        reply_to_comment_text = 'I liked it too.'
        reply_to_reply_text = 'Great insight.'
        
        test_user_3 = User.objects.create(**test_user_3_data)
        
        test_user_4 = User.objects.create(**test_user_4_data)

        test_post_1 = Post.objects.create(user=test_user_1,
                text=post_text, likes=0,
                comments=0, views=0,
                image=None
        )
        
        test_comment_1 = Comment(user=test_user_2,
                                    post=test_post_1,
                                    text=comment_text,
                                    likes=0,
                                    comments=0,
                                    views=0)

        test_reply_1 = Reply(user=test_user_3,
                                parent=test_comment_1,
                                text=reply_to_comment_text,
                                likes=0,
                                comments=0,
                                views=0)

        test_reply_2 = Reply(user=test_user_4,
                                parent=test_reply_1,
                                text=reply_to_reply_text,
                                likes=0,
                                comments=0,
                                views=0)

        print(Reply.objects.all())
        print(Comment.objects.all())
        print('.................objects succefully created....................')



    def delete_all_objects(self):
        User.objects.all().delete()
        Product.objects.all().delete()
        SubCategory.objects.all().delete()
        Category.objects.all().delete()
        Wishlist.objects.all().delete()
        #Notifications.objects.all().delete()
        Post.objects.all().delete()
        Comment.objects.all().delete()
        Reply.objects.all().delete()
        CartOrder.objects.all().delete()
        SingleProductOrder.objects.all().delete()
        BillingInfo.objects.all().delete()
        ShipmentInfo.objects.all().delete()
        print('...................objects succefully deleted...............')
