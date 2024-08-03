from django.test import TestCase
from user.models import User
from .modles import (Post, Comment)

# Create your tests here.
class TestPost(TestCase):

    def setup(self):
        super.setup()
        
        test_user_3_data = {
                        'first_name': 'James',
                        'last_name': 'Trim',
                        'email': 'jamestrim@gmail.com',
                        'password': 'jamestrim27!',
                        'birth_date': '10-10-1990',
                }
        
        test_user_4_data = {
                        'first_name': 'Helena',
                        'last_name': 'Peter',
                        'email': 'helenapet@gmail.com',
                        'password': 'helena27!',
                        'birth_date': '10-10-1993',
                }
        
        post_text = 'Check out this new product.'
        comment_text = 'Its really great.'
        reply_to_comment_text = 'I liked it too.'
        reply_to_reply_text = 'Great insight.'
        
        self.test_user_3 = User.object.create(**test_user_data_3)
        
        self.test_user_4 = User.object.create(**test_user_data_4)

        self.test_post_1 = Post.objects.create(user=self.test_user_1,
                text=text, likes=0,
                comments=0, views=0,
                images=None
        )
        
        self.test_comment_1 = Comment(user=self.test_user_2,
                                    post=self.test_post_1,
                                    text=comment_text,
                                    likes=0,
                                    comments=0,
                                    views=0)

        self.test_reply_1 = Reply(user=self.test_user_3,
                                parent=self.test_comment_1,
                                text=reply_to_comment_text,
                                likes=0,
                                comments=0,
                                views=0)

        self.test_reply_2 = Reply(user=self.test_user_4,
                                parent=self.test_reply_1,
                                text=reply_to_reply_text,
                                likes=0,
                                comments=0,
                                views=0)
    
    def test_post_ok(self):
        
        self.assertEqual(self.test_post_1.user=self.test_user_1)
        self.assertEqual(self.test_post_1.text=text)
        self.assertEqual(self.test_post_1.likes=0)
        self.assertEqual(self.test_post_1.comments=0)
        self.assertEqual(self.test_post_1.views=0)
        self.assertEqual(self.test_post_1.images=None)

    def test_comment_ok(self):
        self.assertEqual(self.test_comment_1.post=self.test_post_1)
        self.assertEqual(self.test_comment_1.text=self.comment_text)
        self.assertEqual(self.test_comment_1.user=self.test_user_2)
        self.assertEqual(self.test_comment_1.likes=0)
        self.assertEqual(self.test_comment_1.comments=0)
        self.assertEqual(self.test_comment_1.views=0)

    def test_reply_to_comment_ok(self):
        self.assertEqual(self.test_reply_1.parent=self.test_comment_1)
        self.assertEqual(self.test_reply_1.text=self.reply_to_comment_text)
        self.assertEqual(self.test_reply_1.user=self.test_user_3)
        self.assertEqual(self.test_reply_1.likes=0)
        self.assertEqual(self.test_reply_1.comments=0)
        self.assertEqual(self.test_reply_1.views=0)

    def test_reply_to_reply_ok(self):
        self.assertEqual(self.test_reply_2.parent=self.test_comment_1)
        self.assertEqual(self.test_reply_2.text=self.reply_to_reply_text)
        self.assertEqual(self.test_reply_2.user=self.test_user_3)
        self.assertEqual(self.test_reply_2.likes=0)
        self.assertEqual(self.test_reply_2.comments=0)
        self.assertEqual(self.test_reply_2.views=0)
