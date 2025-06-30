from appstore import celery_app as app
from django.db import transaction
from cart.models import Cart
from .models import ( Order, PaymentTransaction, Transaction, SupplierPayment, Notification, SupplierWallet )
from decimal import Decimal
from django.db.models import Sum, F
from celery import shared_task

def do_transaction_check(tx_ref, request):

    try:
        transaction = PaymentTransaction.objects.get(tsx_ref=tx_ref)
    except PaymentTransaction.DoesNotExist as e:
        return {'error': str(e)}
    
    if transaction.status == 'success':
        
        try:
            order_data = request.data
            order_model = CartOrder if type == 'cart' else SingleProductOrder
            parent_field = 'product' if type == 'single' else 'cart'
            if order_data:
                billing_info_data = order_data.get('billing_info', None)
                shipment_info_data = order_data.get('shipment_info', None)
                cart_id = order_data.get('cart_id', None)
                product_id = order_data.get('product_id', None)
                parent = Cart.objects.get(pk=cart_id) if type == 'cart' else Product.objects.get(pk=product_id)
                if all([billing_info_data, shipment_info_data, parent]):
                    new_billing_info = SerializeShipment(data=billing_info_data)
                    new_shipment_info = SerializeShipment(data=shipment_info_data)
                    if new_billing_info.is_valid() and new_shipment_info.is_valid():
                        with transaction.atomic():
                            product = Product.objects.select_for_update().get(pk=product_id)
                            new_billing_info = new_billing_info.create()
                            new_shipment_info = new_shipment_info.create()
                            order = model(parent_field=parent, billing_info=new_billing_info, shipment_info=new_shipment_info)
                            order.save()
                            post_save.send(Order, order, request.user)
                            clear_cart.send(Order)
                        return Response({'message': "Order succesfully placed."}, status=status.HTTP_200_OK)
                    
                message = 'Error: order failed, Please check order details.'
                return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Order data not sufficient.'}, status=status.HTTP_400_BAD_REQUEST)

        except (json.JsonDecoderError, ValueError, TypeError) as e:
            message = "Error: couldn't parse values recieved. " + str(e)
            return Response("Order successfully placed.", status=501)
        
        except (IntegrityError, Order.DoesNotExist) as e:
            return Response({'message': 'Unique constrains not provided for payment info.'}, status=status.HTTP_400_BAD_REQUEST)


@app.task(bind=True, max_retries=3)
def schedule_transaction_verification(tx_ref, countdown):
    """Schedule a transaction verification with countdown"""
    
    transaction = Transaction.objects.get(tx_ref=tx_ref)
    if transaction.status == 'pending':
    
        if countdown <= 1200:
            check_transaction_status.delay(tx_ref=tx_ref)
            schedule_transaction_verification.apply_async(
                args=[tx_ref, countdown],
                countdown=countdown * 2
            )


@app.task(bind=True, max_retries=3)
def check_transaction_status(tx_ref, payment_gateway='chapa'):
    
    try:
        transaction = Transaction.objects.get(tx_ref=tx_ref).select_related('order').prefetch_related('order__cart__cart_data_for')

        PG_VERIFICATION_URLS = {
            'chapa': f'https://api.chapa.co/v1/transaction/verify/{tx_ref}',
        }

        PG_PAYMENT_STATUS = {
            'chapa_success': ('success', 'in_progress'),
            'chapa_failed': ('failed', 'failed'),
        }

        url = PG_VERIFICATION_URLS.get(payment_gateway)
        response = requests.get(url=url, headers=HEADERS)
        response_data = response.json()

        # Common update data
        update_data = {
            'payment_gateway_response': response_data,
            'verification_attempts': transaction.verification_attempts + 1,
            'last_verification_time': timezone.now()
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

    except Exception as exc:
        
        return {'error': str(exc)}



@app.task(bind=True, max_retries=3)
def record_supplier_earnings(self, transaction_id):
    """
    Record earnings for suppliers after successful transaction and notify them
    """
    try:
        with transaction.atomic():
            # Get the transaction and related cart order
            transaction = Transaction.objects.select_related('order', 'order__cart').get(id=transaction_id)
            cart_order = transaction.order
            
            # Get all products in the cart with their quantities and prices
            cart_items = cart_order.cart.cart_data_for.select_related('product', 'product__supplier').all()
            
            # Group by supplier and calculate their earnings
            supplier_earnings = {}
            for item in cart_items:
                supplier = item.product.supplier
                item_total = item.quantity * item.product.price
                
                if supplier not in supplier_earnings:
                    supplier_earnings[supplier] = Decimal('0')
                supplier_earnings[supplier] += item_total
            
            # Prepare lists for bulk creation
            supplier_payments = []
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
                
                # Create earning record
                supplier_payments.append(
                    SupplierPayment(
                        supplier=supplier,
                        transaction=transaction,
                        amount=amount,
                        status='pending'
                    )
                )
                
                # Create notification for supplier
                notifications.append(
                    Notification(
                        user=supplier,
                        title='New Earnings Available',
                        message=f'You have earned {amount} from transaction {transaction.tx_ref}.\
                                You can withdraw this amount whenever you want.',
                        type='earnings',
                        priority='medium'
                    )
                )
            
            # Bulk create all records
            SupplierPayment.objects.bulk_create(supplier_payments)
            Notification.objects.bulk_create(notifications)
                
    except Exception as exc:
        # Retry the task with exponential backoff
        self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
