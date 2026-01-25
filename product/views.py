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
from .utils import (SearchEngine, get_populars)
from .tasks import do_popularity_check
from shared.utils import (paginate_queryset)
import json
# Create your views here.

# Use ViewSets and APIViews accordingly.

@method_decorator(csrf_exempt, name='dispatch')
class ProductView(APIView):

    def get_permissions(self):
        path = self.kwargs.get('path', None)
        if not path or path == 'my':
            return [IsAuthenticated()]
        
        return [AllowAny()]


    def get(self, request, path, index, *args, **kwargs):
 
        if path == 'my':
            user_products = get_list_or_404(Product.objects.filter(supplier=request.user).order_by('-created_at'))
            user_products = paginate_queryset(user_products, request, ProductSerializer, 40)
            return Response(user_products.data,
                status=status.HTTP_200_OK)
        
        if path == 'view':
            product = get_object_or_404(Product, pk=index)
            product = ProductSerializer(product)

            return Response(product.data,
                    status=status.HTTP_200_OK)
        
        if path == 'all':
            products = Product.objects.all()
            products = paginate_queryset(products, request, ProductSerializer, 300)
            return Response(products.data, status=status.HTTP_200_OK)

        return Response({'message': 'Page Not Found.'}, status=status.HTTP_404_PAGE_NOT_FOUND)


    def post(self, request, *args, **kwargs):
     
        products = request.data
        
        if not products:
            return Response({'message': 'No product data provided.'}, status=status.HTTP_400_BAD_REQUEST)
    
        for product in products:
            product['supplier'] = request.user.pk
        
        if len(products) > 1:
            many = True
            data = products
        else:
            many = False
            data = products[0]

        serializer = ProductSerializer(data=data, many=many)
        
        if serializer.is_valid() and serializer.bulk_validate_tags():
            try:
                serializer.bulk_create() if len(products) > 1 else serializer.create()
                return Response({'message': 'product successfully added.'}, status=status.HTTP_201_OK)
            except Exception as e:
                return Response({'message': f'product creation unsuccessful. error: {e}'}, status=status.HTTP_401_OK)
        
        return Response({'message': 'product isn\'t added, data validation failed.', 'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
    
        product_data = request.data
        product = get_object_or_404(Product, pk=product_data.get('id'))
        if product.supplier != request.user:
            return Response({'message': 'User not authorized to do the update operation on this product.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = ProductSerializer(data=product_data)

        if serializer.is_valid():
            serializer.update(product)
            return Response({'message': 'product successfully updated.'}, status=status.HTTP_201_CREATED)

        return Response({'message': 'product not updated'}, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, index, *args, **kwargs):
    
        product_data = request.data
        product_id = product_data.get('product_id', None)

        if product_id:
            product = get_object_or_404(Product, pk=product_id)
            if product.supplier == request.user:
                product.delete()
                return Response({'message': 'Product successfully deleted'}, status=status.HTTP_200_OK)
            
            return Response({'message': 'User Not authorized to delete the specified product'}, status=status.HTTP_NOT_AUTHORIZED_401)
                

@method_decorator(csrf_exempt, name='dispatch')
class CategoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, type, id, *args, **kwargs):
        if type == 'all':
            categories = Category.objects.all()
            categories = CategorySerializer(categories, many=True)
            
            return Response(
                categories.data,
                    status=status.HTTP_200_OK)

        if type == 'subcategory':
            
            subcategories = SubCategory.objects.filter(category__id=id).all()
            serialized_subcats = SubCategorySerializer(subcategories, many=True)
            
            return Response(
                    serialized_subcats.data,
                 status=status.HTTP_200_OK)
            
        if type == 'new':
            
            month_ago = datetime.today() - timedelta(days=30)
            category_id = request.GET.get('category_id')
            if category_id:
                new_in_category_metrics = Metrics.objects.filter(
                    product__subcategory__category__id=category_id,
                        date_added__gte=month_ago).values('product__id', 'product__name', 'product__description', 'product__price', 'product__image').annotate(purchases=Sum('qunatity'),
                                ).filter(purchases__gte=200).order_by('-purchases')

                return Response(
                    new_in_category_metrics.data,
                        status=status.HTTP_200_OK)

        if type == 'products':
            cat_id = request.GET.get('category_id', None)
            if cat_id:
                queryset = Product.objects.filter(subcategory__category__id=cat_id).order_by('-quantity')
                
                products = get_list_or_404(queryset)
                
                paginated_products = paginate_queryset(products, request, ProductSerializer, 40)
                
                return Response({
                    'products': paginated_products.data
                    }, status=status.HTTP_200_OK)

        return Response({
            'message': 'wrong uri.'},
            status=status.HTTP_404_PAGE_NOT_FOUND)


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
                products = Product.objects.filter(sub_category__pk=subcat_id).order_by('-created_at')
                products = paginate_queryset(products, request, ProductSerializer, 40)
                return Response(products.data,
                     status=status.HTTP_200_OK)
        
        #add date and cursor pagination
        if type == 'new':
            subcat_id = request.GET.get('subcat_id', None)
            if subcat_id:
                month_ago = datetime.today() - timedelta(days=30)

                new_product_metrics = Metrics.objects.filter(product__sub_category__pk=subcat_id,
                                        product__created_at__gte=month_ago).values('product__id', 'product__name', 'product__price', 'product__description').annotate(purchases=Sum('quantity')).filter(purchases__gte=500).order_by('-purchases')

                return Response(
                    new_product_metrics,
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

        if type == 's':

            subcat_id = request.GET.get('id', None)
            subcat = get_object_or_404(SubCategory, pk=subcat_id)
            tags_for_subcat = subcat.tags.all()

            serialized_tags = paginate_queryset(tags_for_subcat, request, TagSerializer, 50)

            return Response(serialized_tags.data, status=status.HTTP_200_OK)

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
        await asyncio.to_thread(self.get_tokens)
        query_string = request.GET.get('q', None)
        search_type = request.GET.get('type', 'specified')
        index = request.GET.get('index', 1)
        if not (query_string and search_type):
            return Response(data={'message': 'query string can\'t be empty'}, safe=False, status=400)
        search_engine = SearchEngine(query_string, request.user, index)
        if search_type == 'blind':
            results = await search_engine.blind_search
        else:
            results = await search_engine.specified_search
            
        return Response({'data': results}, status=status.HTTP_200_OK)


class Popular(APIView):
    
    permission_classes = [AllowAny]

    def get(self, request, path, *args, **kwargs):
        if path not in ['subcategory', 'category', 'product']:
            return Response({'message': f'Wrong positional parameter {path}'}, status=status.HTTP_404_PAGE_NOT_FOUND)
        populars = get_populars(path, request)
        return Response({'data': populars}, status=status.HTTP_200_OK)
