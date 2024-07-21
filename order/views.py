from django.shortcuts import render
from django.views import View
import json
from cart.models import Cart
from .models import BillingInfo
from .models import PaymentInfo
from .serializers import BaseSerializer
# Create your views here.

class OrderView(View):

    def get(self, *args, **kwargs):

        orders = Order.obects.filter(user=request.user).order_by('date')
        serialized_orders = BaseSerializer(model='order', fields='__all__', many=True) 
 
        if serializers.is_valid():
            return JsonResponse(data=serialized_orders.data, safe=True, status=200)
        return JsonResponse(data=serialized_orders.error, status=501)

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
            return JsopResponse(data={data: None, message: message}, status=501)


class Pay(View):

    def post(request, *args, **kwargs):
        pass
