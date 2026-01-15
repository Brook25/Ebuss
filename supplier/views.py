from django.shortcuts import render
from django.db import transaction
from django.db.models import (Q, F, Prefetch)
from django.core import cache
from django.shortcuts import (get_list_or_404, get_object_or_404)
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework import status
from shared.utils import paginate_queryset
from .metrics import (ProductMetrics, CustomerMetrics)
from order.models import ( CartOrder)
from order.serializers import (CartOrderSerializer)
from .tasks import schedule_withdrawal_verification
from user.serializers import UserSerializer
from .models import SupplierWallet, SupplierWithdrawal, WithdrawalAcct
from .permissions.supplier_permissions import IsSupplier
from product.models import Product
from product.serializers import ProductSerializer
from shared.permissions import IsAuthenticated
from .serializers import InventorySerializer, WalletSerializer, WithdrawalSerializer
from user.models import User
from .utils import set_bank_data
from decimal import Decimal
import uuid
import os
import requests
# Create your views here.

class DashBoardHome(APIView):
    
    permission_classes = [IsAuthenticated, IsSupplier]

    def get(self, request, *args, **kwargs):
        date = datetime.now()
        metrics =  ProductMetrics(request.user, date)
        quarterly_revenue = metrics.get_quarterly_revenue()
        quarterly_metrics =  metrics.get_monthly_metric(quarterly=True)
        hourly_metrics = metrics.hourly_metric()
        cart_orders = CartOrder.objects.filter(supplier=request.user).order_by('-purchase_date')
        cart_order_data = paginate_queryset(cart_orders, request, CartOrderSerializer, 50).data
        inventory_obj = Inventory.objects.filter(product__supplier=request.user).order_by('-date').prefetch_related('product')
        inventory_data = paginate_queryset(inventory_obj, request, InventorySerializer, 50).data
        subscribers = request.user.subscribers.all()
        subscriber_data = paginate_queryset(subscribers, request, UserSerializer, 50).data

        data = {
               'cart_orders': cart_order_data,
               'inventory_data': inventory_data,
               'hourly_metrics': hourly_metrics,
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


class CustomerMetric(APIView):
    
    def get(self, request, year, *args, **kwargs):
        start_date_string = request.GET.get('start_date', None)
        end_date_string = request.GET.get('end_date', None)
        try:
            start_date = datetime.fromisoformat(start_date_string)
            end_date = datetime.fromisoformat(end_date_string)
            year = datetime.fromisoformat(year)
            customer_metrics = CustomerMetric(request.user)
            customer_data = customer_metrics.get_top_customers(start_date, end_date)
            return Response({'success': True, 'data': customer_data}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': True, 'message': f'Wrong datetime format. {e}'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': True, 'message': f'Couldnt retreive customer data.{e}'})


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


class SupplierWalletView(APIView):
    permission_classes = [IsAuthenticated, IsSupplier]

    def get(self, request):
        """Get supplier wallet details"""
        if request.user.role != 'supplier':
            return Response(
                {'error': 'Only suppliers can access wallet details'}, 
                status=status.HTTP_403_FORBIDDEN
            )


        # Get recent withdrawals
        recent_withdrawals = SupplierWithdrawal.objects.filter(
            wallet=wallet
        ).order_by('-created_at')[:15]


        wallet = WalletSerializer(wallet)
        withdrawals = WithdrawalSerializer(recent_withdrawals, many=True)

        return Response({
            'wallet': wallet.data,
            'recent_withdrawals': withdrawals.data
       }, status=status.HTTP_200_OK)

    def _make_transfer(self, amount, withdrawal_acct):
      
        transfer_url = "https://api.chapa.co/v1/transfers"
 
        secret_key = os.getenv('CHAPA_SECRET_KEY', None)
        reference = uuid.uuid4()
        
        if not (withdrawal_acct and secret_key):
            raise ValueError('Wallet and withdrawal account not configured.')
        
        with transaction.atomic(): 
            wallet = SupplierWallet.objects.select_for_update().get(pk=withdrawal_acct.wallet_id)
            if amount > wallet.balance:
                raise ValueError('Insufficient balance') 
            headers = {
                'Authorization': f'Bearer {secret_key}',
                'Content-Type': 'application/json'
            }
            payload = {
                "account_name": withdrawal_acct.holder_name,
                "account_number": withdrawal_acct.account_number,
                "amount": amount,
                "currency": "ETB",
                "reference": reference,
                "bank_code": withdrawal_acct.chapa_bank_id
            }

            response = requests.post(transfer_url, json=payload, headers=headers)

            if response.status_code != 200 or response.json().get('status', None) != 'success':
                raise APIException('Transfer failed. Payment gateway returned failed response.')
            wallet.balance -= amount
            wallet.save()
            withdrawal_data = { 'reference': reference, 'wallet': wallet.pk, 'withdrawal_acct': withdrawal_acct.pk}
            withdrawal = WithdrawalSerializer(data=withdrawal_data)
            if withdrawal.is_valid(raise_exception=True):
                withdrawal.save()
              
            schedule_withdrawal_verification.apply_aync(args=[reference, 10], countdown=10)

        return withdrawal

    def post(self, request):
        """Request a withdrawal"""
        if request.user.role != 'supplier':
            return Response(
                    {'error': 'Only suppliers can request withdrawals'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        amount = request.data.get('amount', None)
        withdrawal_acct_id = request.data.get('withdrawal_acct_id', None)

        if not (amount and withdrawal_acct_id):
            return Response(
                {'error': 'Amount and bank account are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            withdrawal_acct = get_object_or_404(WithdrawalAcct, pk=withdrawal_acct_id)
            amount = Decimal(amount)            
            withdrawal = self._make_transfer(amount, withdrawal_acct)

        except ValueError as err:
            return Response(
                {'error': str(err)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as err:
            return Response(
                {'error': str(err)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'message': 'Withdrawal request submitted successfully',
            'withdrawal_id': withdrawal.id,
            'status': withdrawal.status
        }, status=status.HTTP_201_CREATED)
