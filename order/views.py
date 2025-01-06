from django.views import View
from django.db import transaction
import json
from cart.models import Cart
from product.models import Product
from .models import (BillingInfo, ShipmentInfo, SingleProductOrder, CartOrder)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framwork.status import status
from .serializers import (CartOrderSerializer, SingleProductOrderSerializer,
                          SerializeShipment)
from utils import paginate_queryset
# Create your views here.

class OrderView(APIView):

    def get(self, request, *args, **kwargs):
 
        products = Product.objects.select_related('supplier').only('pk', 'name', 'supplier__username')
        singleProdcuctOrders = SingleProductOrder.objects.filter(user=request.user).order_by('date').prefetch_related(Prefetch('product', queryset=products))
        singleProductOrders = paginate_queryset(singleProductOrders, request, SingleProductOrderSerializer)

        cartOrders = CartOrder.objects.filter(user=request.user).prefetch_related('cart', 
                Prefetch('product', queryset=products))
        cartOrders = paginate_queryset(cartOrders, request, CartOrderSerializer)
        
        return Response({'cart_orders': cartOrders.data,
                            'single_product_orders': singleProductOrders.data}, status=status.HTTP_200_OK)

    def post(self, request, type, *args, **kwargs):

        try:
            order_data = json.loads(request.body)
            model = CartOrder if type == 'cart' else SingleProductOrder
            parent_model = 'product' if type == 'single' else 'cart'
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
                        new_billing_info = new_billing_info.create()
                        new_shipment_info = new_shipment_info.create()
                        order = model(parent_model=parent, billing_info=new_billing_info, shipment_info=new_shipment_info)
                        order.save()
                        return Response({'message': "Order succesfully placed."}, status=status.HTTP_200_OK)
                    
                message = 'Error: order failed, Please check order details.'
                return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Order data not sufficient.'}, status=status.HTTP_400_BAD_REQUEST)

        except json.JsonDecoderError or ValueError or TypeError as e:
            message = "Error: couldn't parse values recieved. " + str(e)
            return Response("Order successfully placed.", status=501)
        
        except IntegrityError as e:
                        return Response({'message': 'Unique constrains not provided for payment info.'}, status=501)


    def delete(self, request, type, id, *args, **kwargs):
        
        if type == 'single':

            with transaction.atomic():
                single_order = SingleProductOrder.objects.filter(pk=id).select_related('product').first()
                if single_order:
                    quantity = single_order.quantity
                    single_order.product.quantity += quantity
                    single_order.product.save()
                    single_order.delete()
                else:
                    return Response('Order not found', status=status.HTTP_400_BAD_REQUEST)
                
        elif type == 'cart':

            with transaction.atomic():
                cart_order = CartData.objects.filter(cart__pk=id).prefetch_related('product', 'quantity')
                if cart_order:
                    for cart_data in cart_order:
                        cart_data.product.quantity += cart_data.quantity
                        cart_data.product.save()
                    cart_order.delete()
                else:
                    return Response('Order not found', status=400)

        return Response('Order successfuly deleted.', status=status.HTTP_200_OK)
            

class Pay(View):

    def post(request, *args, **kwargs):
        pass
