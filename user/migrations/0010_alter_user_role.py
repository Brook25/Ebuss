# Generated by Django 5.0 on 2025-01-24 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_user_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('customer', 'Customer'), ('supplier', 'Supplier'), ('admin', 'Admin')], default='customer'),
        ),
    ]
