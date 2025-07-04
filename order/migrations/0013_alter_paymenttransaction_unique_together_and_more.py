# Generated by Django 5.0 on 2025-06-11 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0012_paymenttransaction_delete_payment'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='paymenttransaction',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='paymenttransaction',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('aborted', 'Aborted'), ('success', 'Success'), ('failed', 'Failed')], max_length=30),
        ),
        migrations.RemoveField(
            model_name='paymenttransaction',
            name='ref_id',
        ),
    ]
