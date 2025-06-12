from appstore import celery_app
from django.db import transaction
from cart.models import Cart
from .models import ( Order, PaymentTransaction )

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
