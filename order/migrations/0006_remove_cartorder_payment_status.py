# Generated by Django 5.0 on 2025-07-18 08:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_alter_transaction_payment_gateway'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartorder',
            name='payment_status',
        ),
    ]
