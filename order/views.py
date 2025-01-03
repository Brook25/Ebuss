from django.shortcuts import render
from django.views import View
from django.db import transaction
import json
from cart.models import Cart
from .models import (BillingInfo, ShipmentInfo, SingleProductOrder, CartOrder)
from serializers import OrderSerializer
from utils import paginate_queryset
# Create your views here.

class OrderView(View):

    def get(self, request, *args, **kwargs):
 
        products = Product.objects.select_related('supplier').only('pk', 'name', 'supplier__username')
        singleProdcuctOrders = SingleProductOrder.objects.filter(user=request.user).order_by('date').prefetch_related(Prefetch('product', queryset=products))
        singleProductOrders = paginate_queryset(singleProductOrders, request, SingleProductOrderSerializer)

        cartOrders = CartOrder.objects.filter(user=request.user).prefetch_related('cart', 
                Prefetch('product', queryset=products))
        cartOrders = paginate_queryset(cartOrders, request, CartOrderSerializer)
        
        return Response({'cart_orders': cartOrders.data,
                            'single_product_orders': singleProductOrders.data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):

        try:
            order_data = json.loads(request.body)
            if order_data:
                billing_info = order_data.get('billing_info', None)
                shipment_info = order_data.get('shipment_info', None)
                cart = order_data.get('cart', None)
                if billing_info and shipment_info and cart:
                    try:
                        new_billing_info = BillingInfo.get_or_create_billing_info(**billing_info)
                        new_shipment_info = ShipmentInfo.get_or_create_shipment_info(**shipment_info)
                        new_cart = Cart(**cart)
                        new_cart.save()
                        request.session.get('carts').pop(cart.get('name', ''))
                        order = Order(cart=new_cart, billing_info=new_billing_info, shipment_info=new_shipment_info)
                        order.save()
                        return JsonResponse(data={data: order.id, message: "Order succesfully placed."}, status=200)
                    except IntegrityError as e:
                        return JsonResponse(data={data: None, message: 'Unique constrains not provided for payment info.'}, status=501)
                else:
                    message = 'Error: order failed, Please check order details.'
                    return JsonResponse(data={data: None, message: message}, status=400)
            else:
                return JsonResponse(data={data: None, message: 'Order data not sufficient.'}, status=400)

        except json.JsonDecoderError or ValueError or TypeError as e:
            message = "Error: couldn't parse values recieved. " + str(e)
            return Response("Order successfully placed.", status=501)


    def delete(self, request, type, id, *args, **kwargs):
        
        if type == 'single':

            with transaction.atomic():
                single_order = SingleProductOrder.objects.filter(pk=id).select_related('product').first()
                if single_order:
                    quantity = single_order.quantity
                    product.quantity += quantity
                    product.save()
                    single_order.delete()
                else:
                    return Response('Order not found', status=400)
                
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
