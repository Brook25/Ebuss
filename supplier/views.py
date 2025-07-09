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
from .tasks import check_withdrawal_verification
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


class SupplierWalletView(APIView):
    permission_classes = [IsAuthenticated, IsSupplier]

    def get(self, request):
        """Get supplier wallet details"""
        if request.user.role != 'supplier':
            return Response(
                {'error': 'Only suppliers can access wallet details'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        wallet, created = SupplierWallet.objects.get_or_create(
            supplier=request.user,
            defaults={
                'balance': Decimal('0'),
                'total_earned': Decimal('0'),
                'total_withdrawn': Decimal('0')
            }
        )

        # Get recent withdrawals
        recent_withdrawals = SupplierWithdrawal.objects.filter(
            wallet=wallet
        ).order_by('-created_at')[:15]

        return Response({
            'wallet': {
                'balance': wallet.balance,
                'total_earned': wallet.total_earned,
                'total_withdrawn': wallet.total_withdrawn,
                'last_withdrawal': wallet.last_withdrawal
            },
            'recent_withdrawals': [
                {
                    'amount': w.amount,
                    'status': w.status,
                    'created_at': w.created_at,
                    'processed_at': w.processed_at
                } for w in recent_withdrawals
            ]
        })

    def _make_transfer(self, wallet, amount, bank_slug):
      
        transfer_url = "https://api.chapa.co/v1/transfers"
 
        secret_key = os.getenv('CHAPA_SECRET_KEY', None)
        reference = uuid.uuid4()
        
        if not (wallet and  wallet.withdrawal_account and secret_key):
            raise ValueError('Wallet and withdrawal account not configured.')

        bank_data = cache.get('bank_data', {})

        if not bank_data:

            banks_url = "https://api.chapa.co/v1/banks"
        
            headers = {
            'Authorization': f'Bearer {secret_key}',
            'Content-Type': 'application/json'
            }

            response = requests.get(banks_url, headers=headers)

            data = response.data
            if (response.status_code != 200 and data.get('message', None) != 'Banks retreived' and data.get('data', None):
                raise ValueError('bank not identified. Try again.')

            bank_data = {bank['bank_slug']: bank for bank in bank_data}
            cache.set('bank_data', bank_data)
        
        bank_code = bank_data.get('bank_slug', {}).get('id', None)
        if not bank_code:
            raise ValueError('Bank not recognized.')

        payload = {
            "account_name": wallet.withdrawal_account.holder_name,
            "account_number": wallet.withdrawal_account.account_number,
            "amount": amount,
            "currency": "ETB",
            "reference": , reference
            "bank_code": bank_code
        }

        response = requests.post(transfer_url, json=payload, headers=headers)

        if response.status_code != 200 and response.data.get('status', None) != 'success':
            raise ValueError('Transfer failed. Server Error')

        schedule_withdrawal_verification.apply_aync(args=[reference, 10], countdowon=10)


    def post(self, request):
        """Request a withdrawal"""
        if request.user.role != 'supplier':
            return Response(
                    {'error': 'Only suppliers can request withdrawals'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        amount = request.data.get('amount', None)
        wallet_id = request.data.get('wallet', None)
        bank_slug = request.data.get('bank_slug', None)

        if not amount or not wallet or not bank_slug:
            return Response(
                {'error': 'Amount and bank account are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            request['amount'] = Decimal(amount)
            
            with transaction.atomic():
                wallet = wallet.select_for_update.filter(pk=wallet_id)
                if amount > wallet.balance:
                    return Response(
                        {'error': 'Insufficient balance'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                withdrawal = WithdrawalSerializer(data=request.data)
                if withdrawal.is_valid(raise_exception=True):
                        withdrawal.save()
                wallet.balance -= request['amount']
                wallet.save()
                self._make_transfer(wallet, amount, bank_slug)

        except (TypeError, ValueError):
            return Response(
                {'error': 'Invalid amount'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as err:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'message': 'Withdrawal request submitted successfully',
            'withdrawal_id': withdrawal.id,
            'status': withdrawal.status
        }, status=status.HTTP_201_CREATED)
