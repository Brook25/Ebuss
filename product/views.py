from django.shortcuts import render
from django_redis import get_redis_connection
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse 
from django.core.paginator import Paginator
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.models import User
import asyncio
from .models import (Product, SubCategory, Category, Tag, TokenToSubCategory)
from .signals import (post_save, post_delete, post_update)
from supplier.models import Inventory
from .serializers import (ProductSerializer, CategorySerializer, SubCategorySerializer, TagSerializer)
from .utils import SearchEngine
from .tasks import do_popularity_check
from utils import paginate_queryset
import json
# Create your views here.


@method_decorator(csrf_exempt, name='dispatch')
class ProductView(APIView):

    @staticmethod
    def validate(products, user):

        subcategory_ids = set([product.get('subcat_id') for product in products])
        subcategories = SubCategory.objects.filter(pk__in=subcategory_ids).prefetch_related('tags')
        subcategories = {subcat.id: subcat for subcat in subcategories}
        for product in products:
            subcat_id = product.get('subcategory_id')
            subcategory = subcategories.get(subcat_id)
            tags = set(product.get('tags').keys())
            subcat_tags = set([name for name, in subcategory.tags.all().values_list('name')])
            if not tags.issubset(subcat_tags):
                return False

        return True
    

    def get(self, request, path, index, *args, **kwargs):
        # add pagination
        
        if path == 'my':
    
            user_products = request.user.products.all().order_by('-date_added')
            user_products = paginate_queryset(user_products, request, ProductSerializer, 40)
            return Response(user_products.data,
                status=status.HTTP_200_OK)
        
        if path == 'view':
            product = Product.objects.filter(pk=index).first()
            # add an option to serializer description, other attrs will be added
            product = ProductSerializer(product)

            return Response(product.data,
                    status=status.HTTP_200_OK)
        
        if path == 'all':
            products = Product.objects.all()
            # add an option to serializer description, other attrs will be added
            products = paginate_queryset(products, request, ProductSerializer, 300)

            return Response(products.data, status=status.HTTP_200_OK)

    def post(self, request, path, *args, **kwargs):
        
        if path == 'my':
            product_data = json.loads(request.body) or {}
            products = product_data.get('products', [])
            if products and ProductView.validate(products, request.user):

                validate_product_data = ProductSerializer(data=products, many=True)
                if validate_product_data.is_valid():
                    created = validate_product_data.bulk_create(products) 
                    return Response({'message': 'product successfully added.'}, status=status.200_HTTP_OK)
        return Response({'message': 'product isn\'t added, data validation failed.'}, status=400)


    def put(self, request, path, *args, **kwargs):
        
        if path == 'my':
            product_data = json.loads(request.body)
            update_data = product_data.get('update_data')
            validate_data = ProductSerializer(data=update_data)

            if validate_data.is_valid():

                product_data.update(product_data)
                return Response({'message': 'product successfully updated.'}, status=status.HTTP_200_OK)

            return Response({'message': 'product not updated'}, status=400)


    def delete(self, request, index, *args, **kwargs):
        
        product_data = json.loads(request.body)
        product_id = product_data.get('product_id', None)

        if product_id:
            product = Product.objects.filter(pk=product_id).first()
            
            if product:
                product.delete()
                return Response({'message': 'Product successfully deleted'}, status=status.HTTP_200_OK)
        return Response({'message': 'Product not deleted'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class CategoryView(View):

    def get(self, request, type, index, *args, **kwargs):
        if type == 'all':
            categories = Category.objects.all()
            categories = CategorySerializer(categories, many=True)
            
            return Response(
                categories.data,
                    status=status.HTTP_200_OK)

        if type == 'subcategory':
            
            subcategories = SubCategory.objects.filter(category__id=index).all()
            serialized_subcats = SubCategorySerializer(subcategories, many=True)
            
            return Response(
                    serialized_subcats.data,
                 status=status.HTTP_200_OK)
            
        if type == 'new':
            
            month_ago = datetime.today() - delta(day=30)
            category_id = request.GET.get('category_id')
            if category_id:
                new_in_category_metrics = Metrics.objects.filter(
                    product__subcategory__category__id=category_id,
                        date_added__gte=month_ago).annotate(purchases=Sum('quantity'), count=Count('product')).filter(purchases__gte=500).select_related('product')

                new_products = [metric.product for metric in new_in_category_metrics]
                products = paginate_queryset(new_products, request, ProductSerializer, 40)
                
                return Response(
                    new_products.data,
                        status=status.HTTP_200_OK)

        if type == 'products':
            cat_id = request.GET.get('category_id', None)
            if cat_id:
                products = Product.objects.filter(subcategory__category__id=cat_id).order_by('-quantity')
 
                products = paginate_queryset(products, request, ProductSerializer, 40)
                return Response({
                    'products': products.data
                    }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class SubCategoryView(View):
    
    def get(self, request, type, index, *args, **kwargs):

        if type == 'all':
            subcategories = SubCategory.objects.all()
            paginated_data = self.paginate(subcategories, 40, index)
            subcat_data = paginated_data.get('values', [])

            serialized_subcat = SubCategorySerializer(subcat_data, many=True)

            return Response({'data': serialized_subcat.data,
                'has_next': paginated_data.get('has_next', False)}, status=HTTP_200_OK)
                
        if type == 'product':
            subcat_id = request.GET.get('subcat_id', None)
            if subcat_id:
                products = SubCategroy.objects.filter(pk=subcat_id).products.all().order_by('-timestamp')
                products = paginate_queryset(products, request, ProductSerializer, 40)
                return Response(products.data,
                     status=stuats.HTTP_200_OK)

        if type == 'new':
            subcat_id = request.GET.get('subcat_id', None)
            if subcat_id:
                month_ago = datetime.today - timedelta(day=30)
                
                new_product_metrics = Metrics.objects.filter(product__subcategory__pk=subcat_id, product__date_added__gte=month_ago).annotate(purchases=Sum('quantity'), count=Count('product')).filter(purchases__gte=500).order_by('-purchases').select_related('product')

                new_product_objs = [new_product_metrics.product for metric in new_product_metrics]
                products = paginate_queryset(new_products, request, ProductSerializer, 40)

                return Response(
                    products.data,
                        status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):

        subcat_data = json.loads(request.body) or {}
        tags = subcat_data.pop('tags')
        validate_subcategory = SubCategorySerialzer(data=subcat_data)

        if validate_subcategory.is_valid():
            category_id = subcat_data.get('category_id')
            new_subcat, created = SubCategory.objects.get_or_create(name=name, category_pk=category_id)
            tags = Tag.objects.filter(pk__in=tags)
            new_subcat.tags.add(*tags)
            return Response({'message': 'new subcategory succefully added'},
                status=status.HTTP_200_OK)

        return Response({'message': 'new subcategory not succefully added'},
                status=501)


@method_decorator(csrf_exempt, name='dispatch')
class TagView(View):

    def get(self, request, type, *args, **kwargs):

        if type == 'all':
 
            tags = Tag.objects.all()
            serialized_tags = TagSerializer(tags, many=True)
            return Response(serialized_tags.data,
                    status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):

        tags = json.loads(request.body) or {}
        tags = tags.get('tags', [])
        if tags:
            tags = Tag.objects.bulk_create([Tag(name=tag) for tag in tags])
            return Response({'message': 'data successfully added'}, status=status.HTTP_200_OK)
        return Response({'message': 'data not successfully added'}, status=status.HTTP_200_OK)


    def delete(self, request, *args, **kwargs):

        tag_data = json.loads(request.body) or {}
        tag = tag_data.get('id')
        if tag_data and tag:
            Tag.objects.filter(pk=id).first().delete()
            return Response({'message': 'Tag succefully deleted.'}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Tag not succefully deleted.'}, status=400)



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
            return Response(data, status=status.HTTP_200_OK)

        if path == 'subcategory':
            subcat_id = request.GET.get('subcat_id', None)
            if subcat_id:
                subcat = SubCategory.objects.filter(pk=subcat_id)
                products_in_subcat = subcat.products.filter(pk__in=popular_products).all()
                popular_products = ProductSerializer(products_in_subcat, many=True)
                data = {'popular_products': popular_products.data}
                return Response(data, status=status.HTTP_200_OK)
        
        if path == 'category':
            cat_id = request.GET.get('cat_id', None)
            if cat_id:
                popular_in_cat = Product.objects.filter(subcategory__category__pk=cat_id, pk__in=popular_products) 
                popular_products = ProductSerializer(popular_in_cat, many=True)
                data = {'popular_products': popular_products.data}
                return Response(data, status=status.HTTP_200_OK)
