from datetime import (datetime, timedelta)
from django_redis import get_redis_connection
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import (Sum, Count) 
from django.shortcuts import (get_list_or_404, get_object_or_404)
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticated, AllowAny)
from rest_framework import status
from user.models import User
import asyncio
from .models import (Product, SubCategory, Category, Tag, TokenToSubCategory)
from supplier.models import Inventory
from .serializers import (ProductSerializer, CategorySerializer, SubCategorySerializer, TagSerializer)
from shared.permissions import IsAdmin
from supplier.models import Metrics
from .utils import SearchEngine
from .tasks import do_popularity_check
from shared.utils import (paginate_queryset, get_populars)
import json
# Create your views here.


@method_decorator(csrf_exempt, name='dispatch')
class ProductView(APIView):

    def get_permissions(self):
        path = self.kwargs.get('path', None)
        if not path or path == 'my':
            return [IsAuthenticated()]
        
        return [IsAdmin()]


    def get(self, request, path, index, *args, **kwargs):
 
        if path == 'my':

            user_products = get_list_or_404(Product.objects.filter(supplier=request.user).order_by('-created_at'))
            user_products = paginate_queryset(user_products, request, ProductSerializer, 40)
            return Response(user_products.data,
                status=status.HTTP_200_OK)
        
        if path == 'view':
            product = get_object_or_404(Product.objects.get(pk=index))
            product = ProductSerializer(product)

            return Response(product.data,
                    status=status.HTTP_200_OK)
        
        if path == 'all':
            products = Product.objects.all()
            products = paginate_queryset(products, request, ProductSerializer, 300)
            return Response(products.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
     
        product_data = request.data
        products = product_data.get('products', [])
        serializer = ProductSerializer(data=products, many=True)
        if serializer.is_valid():
            created = serializer.bulk_create(products) 
            return Response({'message': 'product successfully added.'}, status=status.HTTP_200_OK)
        return Response({'message': 'product isn\'t added, data validation failed.'}, status=400)


    def put(self, request, *args, **kwargs):
    
        product_data = request.data
        update_data = product_data.get('update_data', {})
        product_exists = Product.objects.filter(pk=update_data.get('id'), user=request.user).exists
        if product_exists:
            serializer = ProductSerializer(data=update_data)

            if serializer.is_valid():

                serializer.update()
                return Response({'message': 'product successfully updated.'}, status=status.HTTP_200_OK)

        return Response({'message': 'product not updated'}, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, index, *args, **kwargs):
    
        product_data = request.data
        product_id = product_data.get('product_id', None)

        if product_id:
            product = get_object_or_404(Product, pk=product_id)
            product.delete()
            return Response({'message': 'Product successfully deleted'}, status=status.HTTP_200_OK)
        

@method_decorator(csrf_exempt, name='dispatch')
class CategoryView(APIView):
    permission_classes = [AllowAny]

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
            
            month_ago = datetime.today() - timedelta(day=30)
            category_id = request.GET.get('category_id')
            if category_id:
                new_in_category_metrics = Metrics.objects.filter(
                    product__subcategory__category__id=category_id,
                        date_added__gte=month_ago).annotate(count=Count('product'), purchases=Sum('qunatity'),
                                ).filter(purchases__gte=200).order_by('purchases').select_related('product')

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

        return Response({
            'error': 'wrong path.'},
            status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class SubCategoryView(APIView):
    
    def get_permissions(self):
        
        if self.request.method == 'post':
            return [IsAdmin()]
        return [AllowAny()]

    def get(self, request, type, index, *args, **kwargs):

        if type == 'all':
            subcategories = SubCategory.objects.all()
            paginated = paginate_queryset(subcategories, request, SubCategorySerializer, 40)

            return Response(paginated.data, status=status.HTTP_200_OK)
                
        if type == 'product':
            subcat_id = request.GET.get('subcat_id', None)
            if subcat_id:
                products = SubCategory.objects.filter(pk=subcat_id).products.all().order_by('-timestamp')
                products = paginate_queryset(products, request, ProductSerializer, 40)
                return Response(products.data,
                     status=status.HTTP_200_OK)

        if type == 'new':
            subcat_id = request.GET.get('subcat_id', None)
            if subcat_id:
                month_ago = datetime.today - timedelta(day=30)
                
                new_product_metrics = Metrics.objects.filter(product__subcategory__pk=subcat_id,
                                        product__date_added__gte=month_ago).annotate(count=Count('product'),
                                                purchases=Sum('quantity'),
                                            ).filter(purchases__gte=500).order_by('-purchases').select_related('product')

                new_product_objs = [metric.product for metric in new_product_metrics]
                products = paginate_queryset(new_product_objs, request, ProductSerializer, 40)

                return Response(
                    products.data,
                        status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):

        subcat_data = request.data
        tags = subcat_data.pop('tags')
        validate_subcategory = SubCategorySerializer(data=subcat_data)

        if validate_subcategory.is_valid():
            category_id = subcat_data.get('category_id')
            name = subcat_data.get('name')
            new_subcat, _ = SubCategory.objects.get_or_create(name=name, category_pk=category_id)
            tags = Tag.objects.filter(pk__in=tags)
            new_subcat.tags.add(*tags)
            return Response({'message': 'new subcategory succefully added'},
                status=status.HTTP_200_OK)

        return Response({'message': 'new subcategory not succefully added'},
                status=400)


@method_decorator(csrf_exempt, name='dispatch')
class TagView(APIView):

    permission_classes = [IsAdmin]

    def get(self, request, type, *args, **kwargs):

        if type == 'all':
 
            tags = Tag.objects.all()
            serialized_tags = TagSerializer(tags, many=True)
            return Response(serialized_tags.data,
                    status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):

        tags = request.data
        tags = tags.get('tags', [])
        if tags:
            tags = Tag.objects.bulk_create([Tag(name=tag) for tag in tags])
            return Response({'message': 'data successfully added'}, status=status.HTTP_200_OK)
        return Response({'message': 'data not successfully added'}, status=status.HTTP_200_OK)


    def delete(self, request, *args, **kwargs):

        tag_data = request.data
        tag = tag_data.get('id')
        if tag_data and tag:
            Tag.objects.filter(pk=id).first().delete()
            return Response({'message': 'Tag succefully deleted.'}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Tag not succefully deleted.'}, status=400)



class Search(APIView):

    permission_classes = [IsAdmin]

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
            

        return Response({'data': results}, status=status.HTTP_200_OK)

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


class Popular(APIView):
    
    permission_classes = [AllowAny]

    def get(self, request, path, *args, **kwargs):
        populars = get_populars(path)
        return Response({'data': populars}, status=status.HTTP_200_OK)
