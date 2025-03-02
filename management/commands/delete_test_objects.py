
from shared.utils import SetupObjects
from django.management.base import BaseCommand
from user.models import (User, Notification, Wishlist)
from product.models import (Product, SubCategory, Category, Tag, Review)
from cart.models import (Cart, CartData)
from post.models import (Post, Comment, Reply)
from order.models import (CartOrder, SingleProductOrder, BillingInfo, ShipmentInfo)
from supplier.models import (Metrics, Inventory)

class DeleteObjs(BaseCommand):

    models = {
            'user': User,
            'notif': Notfication,
            'wishlist': Wishlist,
            'product': Product,
            'subcat': SubCategory,
            'category': Category,
            'tag': Tag,
            'review': Review,
            'cart': Cart,
            'cart_data': CartData,
            'post': Post,
            'comment': Comment,
            'reply': Reply,
            'cart_order': CartOrder,
            'sigle_order': SingleProductOrder,
            'billing_info': BillingInfo,
            'shipment_info': ShipmentInfo
            'metrics': Metrics,
            'inventory': Inventory,
            'all': 'all'
            }

    def add_arguments(self, parser):
        parser.add_argument('model', type=str, help='model type')

    def handle(self, *args, **kwargs):
        model = self.models.get(kwargs['model'], None)
        if model ==  None:
            self.stdout.write(self.style.Error('No model with that name.'))
        elif model == 'all':
            setup = SetupObjects()
            setup.delete_all_objects()
            self.stdout.write(self.style.success(f'{model} object successfully deleted.'))
        else:
            model.objects.all().delete()
            self.stdout.write(self.style.success(f'All objects deleted.'))

