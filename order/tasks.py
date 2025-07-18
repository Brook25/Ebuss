from appstore import celery_app as app
from django.db import transaction
from cart.models import Cart
from user.models import Notification
from .models import ( CartOrder, Transaction)
from product.models import Product
from supplier.models import SupplierWallet
from .serializers import TransactionSerializer
from datetime import datetime
from decimal import Decimal
from django.db.models import Sum, F
from celery import shared_task
import os
import requests

SECRET_KEY = os.getenv('CHAPA_SECRET_KEY')

HEADERS = {
        'Authorization': f'Bearer {SECRET_KEY}',
        'Content-Type': 'application/json'
    }


@app.task(bind=True, max_retries=3)
def schedule_transaction_verification(self, tx_ref, countdown):
    """Schedule a transaction verification with countdown"""
    transaction = Transaction.objects.get(tx_ref=tx_ref)
    if transaction.status == 'pending':
    
        if countdown <= 100:
            check_transaction_status.delay(tx_ref=tx_ref)
            schedule_transaction_verification.apply_async(
                args=[tx_ref, countdown],
                countdown=countdown * 2
            )

@app.task(bind=True, max_retries=3)
def check_transaction_status(self, tx_ref, payment_gateway='chapa'):
    
    try:
        transaction = Transaction.objects.filter(tx_ref=tx_ref).select_related('order').prefetch_related('order__cart__cart_data_for').first()

        PG_VERIFICATION_URLS = {
            'chapa': f'https://api.chapa.co/v1/transaction/verify/{tx_ref}',
        }

        PG_PAYMENT_STATUS = {
            'chapa_success': ('success', 'in_progress'),
            'chapa_failed/cancelled': ('failed', 'failed'),
            'chapa_pending': ('pending', 'pending'),
        }

        url = PG_VERIFICATION_URLS.get(payment_gateway)
        response = requests.get(url=url, headers=HEADERS)
        response_data = response.json()

        # Common update data
        update_data = {
            'payment_gateway_response': response_data,
            'verification_attempts': transaction.verification_attempts + 1,
            'last_verification_time': datetime.now()
        }

        if response.status_code == 200: 
            payment_status = response_data.get('data', {}).get('status', None)
            if payment_status:
                update_data['status'], order_status = PG_PAYMENT_STATUS[(f'{payment_gateway}_{payment_status}')]
                serializer = TransactionSerializer(transaction, data=update_data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                transaction.order.status = order_status
                transaction.order.save()
                if payment_status == 'failed':
                    
                    cart_product_data = {cart_data.product: cart_data.quantity for cart_data in transaction.order.cart.cart_data_for}
                    products = Product.objects.select_for_update().filter(pk__in=cart_product_data.values())
                    
                    for product in products:
                        product.quantity += cart_product_data[product.pk]
                        product.save()

                return serializer.data
              
        else:
            serializer = TransactionSerializer(transaction, data=update_data, partial=True)
            if serializer.is_valid():
                serializer.save()
            
            # get admin users and send them an alarming notification
            admins = User.objects.filter(is_superuser=True)
            message = response_data.get('message', '')
            
            notification_data = {
                'note': f'Transaction error has been recieved from {payment_gateway} on tx_ref {tx_ref} with status code {response.status_code}.\
                reponse message: {message}. Please check and fix it.',
                'type': 'order_status',
                'uri': 'http://localhost/nots/1',
                'priority': 'high'
            }
            
            notification = Notification.objects.create(**notification_data)
            
            for admin in admins:
                admin.notification_for.append(notification)
                admin.save()
            return serializer.data
                    
    except (Transaction.DoesNotExist, CartOrder.DoesNotExist) as e:
        return {'error': str(e)}

@app.task(bind=True, max_retries=3)
def record_supplier_earnings(self, transaction_id):
    """
    Record earnings for suppliers after successful transaction and notify them
    """
    try:
        with transaction.atomic():
            # Get the transaction and related cart order
            txn = Transaction.objects.select_related('order', 'order__cart').get(id=transaction_id)
            cart_order = txn.order
            
            # Get all products in the cart with their quantities and prices
            cart_items = cart_order.cart.cart_data_for.select_related('product', 'product__supplier').all()
            
            # Group by supplier and calculate their earnings
            supplier_earnings = {}
            for item in cart_items:
                supplier = item.product.supplier
                item_total = item.quantity * item.product.price
                
                if supplier not in supplier_earnings:
                    supplier_earnings[supplier] = Decimal('0')
                supplier_earnings[supplier] += item_total * Decimal('0.8')
            
            # Prepare lists for bulk creation
            notifications = []
            
            # Create objects for bulk creation
            for supplier, amount in supplier_earnings.items():
                # Get or create supplier wallet
                wallet, created = SupplierWallet.objects.get_or_create(
                    supplier=supplier,
                    defaults={'balance': amount}
                )
                
                # Add earning to wallet
                if not created:
                    wallet.balance += amount
                    wallet.save()
                
                # Create notification for supplier
                notifications.append(
                    Notification(
                        user=supplier,
                        note=f'You have earned {amount} from transaction {txn.tx_ref}.\
                                You can withdraw this amount whenever you want.',
                        type='earnings',
                        priority='medium',
                        uri=' https://sterling-primarily-lionfish.ngrok-free.app/notif/1'
                    )
                )
            
            # Bulk create all records
            Notification.objects.bulk_create(notifications)
                
    except Exception as exc:
        # Retry the task with exponential backoff
        self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
