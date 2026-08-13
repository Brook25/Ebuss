from .models import (Inventory, Metrics, SupplierWallet, SupplierWithdrawal, WithdrawalAcct)
from shared.serializers import BaseSerializer
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from user.models import User


class MetricSerializer(BaseSerializer):
    product = PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True)
    product_details = ProductSerializer(source='product', simple=True, read_only=True)
    total_amount = serializers.IntegerField(min_value=1)
    total_quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = Metrics
        fields = ['total_quantity', 'product', 'total_amount', 'product_details']


'''class AnnotatedMetricSerializer(MetricSerializer):
    total_quantity = serializers.IntegerField(min_value=1)
    total_amount = serializers.IntegerField(min_value=1)

    class Meta(MetricSerializer):
        fields = MetricSerializer.Meta.fields + ['total_amount', 'total_quantity']
'''


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
    withdrawal_account = PrimaryKeyRelatedField(queryset=SupplierWithdrawal.objects.all())

    class Meta:
        fields = '__all__'
        model = WithdrawalAcct

    def validate(self, attrs):
        wallet = SupplierWallet.objects.filter(wallet=attrs.get('wallet', None)).first()
        if attrs['amount'] > wallet.balance:
            raise serializers.ValidationError('withdrawal amount can\'t be less than wallet balance.')

        if wallet.status == 'suspended':
            raise serializers.ValidationError('Can\'t withdraw from a suspended supplier wallet.')

        return attrs


    class WithdrawalSerializer(BaseSerializer):
        class Meta:
            fields = '__all__'
            model = SupplierWithdrawal