from django.shortcuts import render
from djano_redis import get_redis_connection
from django.http import JsonResponse 
from django.core import Paginator
from .models import Product
from .serailizers import ProductSerializer
from .utils import (n_gram_word_prediction,
        predict_search_string, SearchEngine) 
# Create your views here.


class Product(View):

    def get(self, request, *args, **kwargs):
        # add pagination
        param1, param2 = args
        if type(param1) is str and type(param2) is str:
            if param1 == 'product':
                if param2 != 'all':
                    product = Product.objects.filter(id=param2)
                else if param2 == 'all':
                    page = kwargs.get('page', 0)
                    products = Product.objects.all()
                    paginator = Paginator(products, 60)
                    paginated = paginate('products', paginator, page)
            if param1 == 'subcategory':
                subcategory_id = kwargs.get('subcategory_id', None)
                if param2 == 'product':
                    products = SubCategory.objects.filter(id=subcategory_id).products
                if param2 == 'all':
                    subcategories = SubCategory.objects.all()

            if param1 == 'category':
                category_id = kwargs.get('category_id', None)
                if param2 == 'all':
                    categories = Category.objects.all()
                if param2 == 'subcategory' and category_id:
                    subcategories = Category.objects.filter(id=category_id).subcategories
                if param2 == 'product' and category_id:
                    subcategories = Category.objects.filter(id=category_id).subcategories
                    products = [*(subcategory.products) for subcategory in subcategories]
                else:
                    category = Category.objects.filter(id=args[1])

            if param1 == 'new':
                # get popular or trending products from the category or subcat
                month_ago = datetime.today() - delta(day=30)
                if param2 == 'category':
                    category_id = kwargs.get('category_id', None)
                    if category_id:
                        new_in_category = Product.objects.filter(
                                subcategory__parent_id=category_id).filter(
                                        date_added__gte=month_ago) # filter by date

                if param2 == 'subcategory':
                    subcategory_id = kwargs.get('subcategory_id', None)
                    if subcategory_id:
                        new_in_subcategory = SubCategory.objects.filter(
                                id=subcategory_id).products.filter(
                                        date_added__gte=month_ago) # filter by date


    def post(self, request, *args, **kwargs):

        product_details = json.loads(request.body)
        if args[1] == 'add' and validate(**product_details):
            kwargs['supplier'] = request.user
            Product.create(**kwargs).save()
            return JsonResponse(data={'data': None, 'message': 'product successfully added.'}, status=200)
        return JsonResponse(data={'data': None, 'message': 'product isn\'t added'}, status=200)


    @staticmethod
    def validate(**kwargs):
        subcategory_id = kwargs.get('subcategory_id', None)
        quantity = kwargs.get('quantity', None)
        price = kwargs.get('price', None)
        if subcategory_id and quantity and price:
            subcategory = SubCategory.objects.filter(pk=subcategory_id)
            product_name = kwargs.get('product_name', None)
            if product_name:
                tags = kwargs.tags.values()
                if subcategory and set(tags) <= set(subcategory.tags):
                    return True
        return False
        
    @staticmethod
    def paginate(model, paginator, page):
        paginated = paginator.get_page(page)
        values = paginated.object_list
        has_next = paginated.has_next()
        return {'page': paginated, model: values, 'has_next': has_next}


class Search(view):

    async def get(self, request, *args, **kwargs):
        query_string = json.loads(kwargs.get('q', None))
        search_type = json.loads(kwargs.get('type'), None)
        if not (query_string and search_type):
            return JsonResponse(data={data: None, message: 'query string can\'t be empty'}, status=400)
        search_engine = SearchEngine(query_string)
        if search_type == 'blind':
            results = await search_engine.blind_search
        else:
            results = await search_engine.specified_search


class Popular(View):

    def get(self, request, *args, **kwargs):
        # popular done deals
        # Implement celery here
        redis_client = get_redis_connection('default')
        popular_deals = redis_client.lrange('popular', 0, -1)
        # generting url from registered views and adding pagination
        url = reverse('popular-product', kwarg={'page': args[0] + 1})
        data = {'popular_deals': popular_deals, url: url}
        return JsonResponse(data=data, status=200)
