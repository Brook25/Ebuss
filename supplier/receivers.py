from django.dispatch import receiver
from product.signals import post_save
from product.models import Product
from .models import Inventory
from .serializers import InventorySerializer

@receiver(post_save, sender=Product)
def post_product_save(sender, instance, reason, quantity_before, quantity_after, **kwargs):
   
    many_instances = kwargs.get('many', False)
    inventory_data = { 'quantity_before': quantity_before, 'quantity_after': quantity_after,
                            'reason': reason, 'adjustment': quantity_after + quantity_before }
    
    if many_instances and isinstance(instance, list):
        inventory_data = [Inventory.objects(**inventory_data.update({'product': product})) for product in instance]
        validate_inventory_data = InventorySerializer(data=inventory_data, many=True)
        if validate_inventory_data.is_valid():
            Inventory.objects.bulk_create(inventory_data)

    else:
        inventory_data['product'] = instance
        validate_inventory_data = InventorySerializer(data=inventory_data)
        if validate_inventory_data.is_valid():
            Inventory.objects.create(**inventory_data)
