# Generated by Django 5.0 on 2025-07-11 18:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0002_initial'),
        ('supplier', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='metrics',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_metrics', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='metrics',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_metrics', to='product.product'),
        ),
        migrations.AddField(
            model_name='metrics',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supplier_metrics', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='supplierwallet',
            name='supplier',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='wallet', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='withdrawalacct',
            name='wallet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='withdrawal_accounts', to='supplier.supplierwallet'),
        ),
        migrations.AddField(
            model_name='supplierwithdrawal',
            name='withdrawal_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='withdrawals', to='supplier.withdrawalacct'),
        ),
        migrations.AddIndex(
            model_name='supplierwallet',
            index=models.Index(fields=['supplier'], name='supplier_su_supplie_c125c3_idx'),
        ),
        migrations.AddIndex(
            model_name='supplierwallet',
            index=models.Index(fields=['is_active'], name='supplier_su_is_acti_0ab8be_idx'),
        ),
        migrations.AddIndex(
            model_name='supplierwithdrawal',
            index=models.Index(fields=['withdrawal_account'], name='supplier_su_withdra_3521c9_idx'),
        ),
        migrations.AddIndex(
            model_name='supplierwithdrawal',
            index=models.Index(fields=['status'], name='supplier_su_status_8ab95e_idx'),
        ),
    ]
