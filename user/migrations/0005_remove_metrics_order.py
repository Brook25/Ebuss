# Generated by Django 5.0.7 on 2024-08-11 16:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_remove_history_cart_remove_inventory_current_stoke_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='metrics',
            name='order',
        ),
    ]
