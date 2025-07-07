from .models import (Inventory, Metrics, SupplierWallet, WithdrawalAcct)
from shared.serializers import BaseSerializer
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from user.models import User


class MetricSerializer(BaseSerializer):
    product = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    iorder = serializers.SerializerMethodField()

    class Meta:
        model = Metrics
        fields = ['quantity', 'product', 'customer', 'supplier', 'order', 'total_price']

    def get_customer(self, obj):
        return { 'customer_name': obj.customer.name,
                 'customer_id': obj.customer.id
               }

    def get_product(self, obj):
        return { 'product_name': obj.product.name,
                 'product_id': obj.product.id
               }
    def get_order(self, obj):
        return { 'order_id': obj.order.id }

class AnnotatedMetricSerializer(MetricSerializer):
    month = serializers.IntegerField(min_value=1)
    count = serializers.IntegerField(min_value=1)
    total_purchases = serializers.IntegerField(min_value=1)

    class Meta(MetricSerializer):
        fields = MetricSerializer.Meta.fields + ['month', 'count', 'total_purchases']


class InventorySerializer(BaseSerializer):
    product = serializers.SerializerMethodField()
    
    class Meta:
        model = Inventory
        fields = ['date', 'product', 'adjustment', 'quantity_before', 'quantity_after', 'reason']

    def get_product(self, obj):
        return { 'product_name': obj.product.name,
                 'product_id': obj.product.id
               }

class WalletSerializer(BaseSerializer):
    supplier = PrimaryKeyRelatedField(queryset=User.objects.filter(is_supplier=True))

    class Meta:
        fields = '__all__'
        model = SupplierWallet

class WithdrawalAcctSerializer(BaseSerializer):
    wallet = PrimaryKeyRelatedField(queryset=SupplierWaller.objects.all())

    class Meta:
        fields = '__all__'
        model = WithdrawalAcct

    def validate(self, attrs):
       wallet = SupplierWallet.objects.filter(wallet=attrs.get('wallet', None)).first()
       if attrs['amount'] > wallet.balance:
            rasie serializers.ValidationError('withdrawal amount can\'t be less than wallet balance.')

        if wallet.status == 'suspended':
            raise serializers.ValidationError('Can\'t withdraw from a suspended supplier wallet.')

        return attrs
