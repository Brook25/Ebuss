
from shared.utils import SetupObjects
from django.core.management.base import BaseCommand
from user.models import (User, Notification, Wishlist)
from product.models import (Product, SubCategory, Category, Tag, Review)
from cart.models import (Cart, CartData)
from post.models import (Post, Comment)
from order.models import (CartOrder, SingleProductOrder, BillingInfo, ShipmentInfo)
from supplier.models import (Metrics, Inventory)

class Command(BaseCommand):

    models = {
            'user': User,
            'notif': Notification,
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
            'cart_order': CartOrder,
            'sigle_order': SingleProductOrder,
            'billing_info': BillingInfo,
            'shipment_info': ShipmentInfo,
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
            return None
        elif model == 'all':
            setup = SetupObjects()
            setup.delete_all_objects()
        else:
            model.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'{model} object successfully deleted.'))

