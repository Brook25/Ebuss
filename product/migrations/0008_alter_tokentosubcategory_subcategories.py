# Generated by Django 5.0 on 2024-10-21 19:33

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_tokentosubcategory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tokentosubcategory',
            name='subcategories',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), default=list, size=None),
        ),
    ]