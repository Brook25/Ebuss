from django.shortcuts import render
from django_redis import get_redis_connection
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse 
from django.core.paginator import Paginator
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from user.models import User
import asyncio
from .models import (Product, SubCategory, Category, Tag, TokenToSubCategory)
from .serializers import (ProductSerializer, CategorySerializer, SubCategorySerializer, TagSerializer)
from .utils import SearchEngine
from .tasks import do_popularity_check
from utils import paginate_queryset
import json
# Create your views here.


@method_decorator(csrf_exempt, name='dispatch')
class ProductView(APIView):

    @staticmethod
    def validate(products):
        subcat_ids = []
        for prod in products:
            subcat_id = prod.get('subcategory', None)
            if not subcat:
                return False
            subcat_ids.append(subcat_id)
        subcategory_objs = SubCategory.objects.filter(pk__in=subcat_ids).prefetch_related('tags')
        product_data = []
        for subcat in subcategory_objs:
            product = filter(lambda product: product['subcategory'] == subcat.id, products)
            product['subcategory'] = subcat
            product_data.append(product)

        for product in product_data:
            quantity = product.get('quantity', None)
            price = product.get('price', None)
            product_name = product.get('name', None)
            if not (quantity and price and quantity):
                return False
            tags = list(product.get('tags').keys())
            subcat_tags = [name for name, in subcategory.tags.all().values_list('name')]
            if not tags.issubset(subcat_tags):
                return False
        products = product_data
        return True
    

    def get(self, request, path, index, *args, **kwargs):
        # add pagination
        
        if path == 'my':
            # get user
            #user = request.user
            user = User.objects.filter(username='emilyjim1').first()
            user_products = user.products.all().order_by('-date_added')
            user_products = paginate_queryset(user_products, request, ProductSerializer)
            return Response({
                'products': 'data successfully retreived'
                }, 
                status=status.200)
        
        if path == 'view':
            product = Product.objects.filter(pk=index).first()
            # add an option to serializer description, other attrs will be added
            product = ProductSerializer(product)

            return Response(data={
                'product': product.data
                }, status=200, safe=False)
        
        if path == 'all':
            product = Product.objects.all()
            # add an option to serializer description, other attrs will be added
            product = ProductSerializer(product, many=True)

            return JsonResponse(data={
                'product': product.data
                }, status=200, safe=False)
            

    def post(self, request, path, *args, **kwargs):
        
        if path == 'my':
            user = User.objects.filter(username='emilyjim1').first()
            product_data = json.loads(request.body) or {}
            products = product_data.get('products', [])
            if products and ProductView.validate(products):
                prodcts = list(map(lambda prod: prod.update({'supplier': user}), products))
                Product.objects.bulk_create([Product(**prod) for prod in products])
                return Response({'message': 'product successfully added.'}, status=status.200_HTTP_OK)
        return Response({'message': 'product isn\'t added, data validation failed.'}, status=400)


        



@method_decorator(csrf_exempt, name='dispatch')
class CategoryView(View):

    def get(self, request, type, index, *args, **kwargs):
        if type == 'all':
            categories = Category.objects.all()
            categories = CategorySerializer(categories, many=True)
            
            return Response({
                'categories': categories.data,
                }, status=200)

        if type == 'subcategory':
            #cat_id = request.GET.get('cat_id', None)
            subcategories = SubCategory.objects.filter(category__id=index).all()
            serialized_subcats = SubCategorySerializer(subcategories, many=True)
            return Response({
                    'subcategories': serialized_subcats.data,
                }, safe=False, status=200)
            
        if type == 'new':
            # get popular or trending products from the category or subcat
            month_ago = datetime.today() - delta(day=30)
            category_id = request.GET.get('category_id')
            if category_id:
                new_in_category = Metrics.objects.annotate(purchases=Sum('quantity'), count=Count('product')).filter(
                    product__subcategory__category__id=category_id).filter(
                        date_added__gte=month_ago).prefetch_related('products') # filter by date

                paginator = Paginator(new_in_category, 30)
                paginated = paginator.page(index)
                new_products = paginated.object_list
                
                new_products = ProductSerializer(new_products, many=True)
                
                return Response(data={
                    'new_products': new_products.data
                    }, safe=False, status=200)

        if type == 'products':
            cat_id = request.GET.get('category_id', None)
            if cat_id:
                products = Product.objects.filter(subcategory__category__id=cat_id).order_by('-quantity')
                
                paginator = Paginator(products_category, 30)
                paginated = paginator.page(index)
                products = paginated.object_list
                
                products = ProductSerializer(products, many=True)

                return Response({
                    'products': products.data
                    }, safe=False, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class SubCategoryView(View):
    

    def get(self, request, type, index, *args, **kwargs):
        if type == 'all':
            subcategories = SubCategory.objects.all()
            paginated_data = self.paginate(subcategories, 40, index)
            subcat_data = paginated_data.get('values', [])

            serialized_subcat = SubCategorySerializer(subcat_data, many=True)

            return Response({'data': serialized_subcat.data,
                'has_next': paginated_data.get('has_next', False)}, safe=False, status=200)
                
        if type == 'product':
            subcat_id = request.GET.get('subcat_id', None)
            if subcat_id:
                products = SubCategroy.objects.filter(pk=subcat_id).products.all().order_by('-timestamp')
                paginated_data = paginate(products, 50, index)
                product_data = paginated_data.get('values', [])

                serialized_products = ProductSerializer(product_data, many=True)

                return Response({ 'data': serialized_products.data,
                    'has_next': product_data.get('has_next', False) }, status=200, safe=False)

        if type == 'new':
            subcat_id = request.GET.get('subcat_id', None)
            if subcat_id:
                month_ago = datetime.today - timedelta(day=30)
                new_products = Metrics.objects.annotate(purchases=SUM('quantity'), count=COUNT('product')) \
                    .filter(product__subcategory__pk=subcat_id) \
                        .filter(product__date_added__gte=month_ago).prefetch_related('product')

                paginated_data = paginate(new_products, 30, index)
                new_products = paginated_data.get('values', [])

                return JsonResponse(data={
                    'data': new_products,
                    'has_next': paginated_data.get('has_next')
                    }, safe=False, status=200)

    def post(self, request, *args, **kwargs):
        subcat_data = json.loads(request.body) or {}
        name = subcat_data.get('name', None)
        category = subcat_data.get('cat_id', None)
        tags = subcat_data.get('tags', [])
        if name and category and tags:
            category = Category.objects.filter(pk=category).first()
            new_subcat, created = SubCategory.objects.get_or_create(name=name, category=category)
            tags = Tag.objects.filter(pk__in=tags)
            new_subcat.tags.add(*tags)
            return JsonResponse(data={'message': 'new subcategory succefully added'},
                safe=False, status=200)

        return JsonResponse(data={'message': 'new subcategory not succefully added'},
            safe=False, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class TagView(View):

    def get(self, request, type, *args, **kwargs):

        if type == 'all':
            tags = Tag.objects.all()
            serialized_tags = TagSerializer(tags, many=True)
            return JsonResponse(data={'tags': serialized_tags.data}, safe=False,
                    status=200)

    def post(self, request, *args, **kwargs):
        
        tags = json.loads(request.body) or {}
        tags = tags.get('tags', [])
        if tags:
            tags = Tag.objects.bulk_create([Tag(name=tag) for tag in tags])
            return JsonResponse(data={'message': 'data successfully added'}, safe=False, status=200)
        return JsonResponse(data={'message': 'data not successfully added'}, safe=False, status=200)

    def delete(self, request, *args, **kwargs):

        tag_data = json.loads(request.body) or {}
        tag = tag_data.get('id')
        if tag_data and tag:
            Tag.objects.filter(pk=id).first().delete()
            return JsonResponse(data={'message': 'Tag succefully deleted.'})
        return JsonResponse(data={'message': 'Tag succefully deleted.'})



class Search(View):

    async def get(self, request, *args, **kwargs):
        user = await asyncio.to_thread(self.get_user)
        await asyncio.to_thread(self.get_tokens)
        query_string = request.GET.get('q', None)
        search_type = request.GET.get('type', 'specified')
        index = request.GET.get('index', 1)
        if not (query_string and search_type):
            return JsonResponse(data={data: None, message: 'query string can\'t be empty'}, safe=False, status=400)
        search_engine = SearchEngine(query_string, user, index)
        if search_type == 'blind':
            results = await search_engine.blind_search
        else:
            results = await search_engine.specified_search
            

        return Response({'data': results}, status=200)

    def get_user(self):
        return User.objects.filter(username='emilyjim1').first()

    def get_tokens(self):
        TokenToSubCategory.objects.all().delete()
        new_token_1 = TokenToSubCategory.objects.create(**{'token': 'Aurora'})
        new_token_1.subcategories.append('phone')
        new_token_2 = TokenToSubCategory.objects.create(**{'token': '64GB'})
        new_token_2.subcategories.append('phone')
        new_token_3 = TokenToSubCategory.objects.create(**{'token': '14Mp'})
        new_token_3.subcategories.append('phone')
        new_token_4 = TokenToSubCategory.objects.create(**{'token': 'android13'})
        new_token_4.subcategories.append('phone')
        new_token_1.save()
        new_token_2.save()
        new_token_3.save()
        new_token_4.save()
        print(TokenToSubCategory.objects.all().values('token', 'subcategories'))



class Popular(View):

    def get(self, request, path, *args, **kwargs):
        redis_client = get_redis_connection('default')
        popular_products = redis_client.lrange('popular', 0, -1)
        
        if path == 'products':
            popular_products = Product.objects.filter(pk__in=popular_products).all()
            popular_products = ProductSerializer(popular_products, many=True)
            data = {'popular_products': popular_products.data}
            return JsonResponse(data=data, safe=False, status=200)

        if path == 'subcategory':
            subcat_id = request.GET.get('subcat_id', None)
            if subcat_id:
                subcat = SubCategory.objects.filter(pk=subcat_id)
                products_in_subcat = subcat.products.filter(pk__in=popular_products).all()
                popular_products = ProductSerializer(products_in_subcat, many=True)
                data = {'popular_products': popular_products.data}
                return JsonResponse(data=data, safe=False, status=200)
        
        if path == 'category':
            cat_id = request.GET.get('cat_id', None)
            if cat_id:
                popular_in_cat = Product.objects.filter(subcategory__category__pk=cat_id, pk__in=popular_products) 
                popular_products = ProductSerializer(popular_in_cat, many=True)
                data = {'popular_products': popular_products.data}
                return JsonResponse(data=data, safe=False, status=200)

