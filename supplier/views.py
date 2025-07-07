from django.shortcuts import render
from django.db.models import (Q, F)
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from shared.utils import paginate_queryset
from .metrics import ProductMetrics
from order.models import ( CartOrder)
from order.serializers import (CartOrderSerializer)
from user.serializers import UserSerializer
from .permissions.supplier_permissions import IsSupplier
from product.models import Product
from product.serializers import ProductSerializer
from shared.permissions import IsAuthenticated
from .serializers import InventorySerializer
from user.models import User
# Create your views here.

class DashBoardHome(APIView):
    
    permission_classes = [IsAuthenticated, IsSupplier]

    def get(self, request, *args, **kwargs):
        date = request.GET.get('date', '')
        products = request.GET.get('products', [])
        users = User.objects.values('name', 'pk')
        products = Product.objects.values('name', 'pk')
        metrics =  ProductMetrics(request.user, date, products).prefetch_related(Prefetch('user', queryset=users), Prefetch('product', queryset=products))
        quarterly_revenue = metrics.quarterly_metrics()
        quarterly_metrics =  metrics.yearly_metrics(request.user, date, quarterly=True)
        cart_orders = CartOrder.objects.filter(supplier=request.user).order_by('-purchase_date')
        cart_order_data = paginate_queryset(cart_orders, request, CartOrderSerializer).data
        inventory_obj = Inventory.objects.filter(product__supplier=request.user).order_by('-date').prefetch_related(Prefetch('product', queryset=products))
        inventory_data = paginate_queryset(inventory_obj, request, InventorySerializer).data
        subscribers = request.user.subscribers.all()
        subscriber_data = paginate_queryset(subscribers, request, UserSerializer, 50).data

        data = {
               'cart_orders': cart_order_data,
               'inventory_data': inventory_data,
                'quarterly_revenue': quarterly_revenue,
                'quarterly_metrics': quarterly_metrics,
                'subscribers': subscriber_data
               }
        return Response(data, status.HTTP_200_OK)

class DashBoardDate(APIView):
    
    permission_classes = [IsAuthenticated, IsSupplier]

    def get(self, request, period, *args, **kwargs):
        
        date = request.GET.get('date', None)
        metric_obj = ProductMetrics(request.user, date)
        query_params = {key: request.GET.getlist(key) for key in request.GET.keys() if key != 'date'}
        if period == 'daily':
            month = request.GET.get('month', date.today().month)
            metric_data = metric_obj.get_daily_metric(month, **query_params)
        elif period == 'monthly':
            metric_data = metric_obj.get_monthly_metric(**query_params)
        elif period == 'yearly':
            metric_data = metric_obj.get_yearly_metric(**query_params)
        elif period == 'hourly':
            metric_data = metric_obj.get_hourly_metric(**query_params)
        elif period == 'popularity':
            product = request.GET.get('product')
            metric_data = metric_obj.popularity_metric(product)

        return Response(metric_data, status=status.HTTP_200_OK)
        


class Store(APIView):
    
    permission_classes = [IsAuthenticated, IsSupplier]
    
    def get(self, request, *args, **kwargs):
        
        products = Product.objects.filter(supplier=request.user, quantity__gt=0).order_by('-date_added')
        paginated_products = paginate_queryset(products, request, ProductSerializer, 60)
        return Response(paginated_products, status=status.HTTP_200_OK)



class Inventory(APIView):
    
    permission_classes = [IsAuthenticated, IsSupplier]
    
    def get(self, request, *args, **kwargs):
        
        inventory = Inventory.objects.filter(product__supplier=request.user).order_by('-date')
        paginated_inventory = paginate_queryset(inventory, request, InventorySerializer, 100)
        return Response(paginated_inventory, status=status.HTTP_200_OK)
