# Generated by Django 4.2.5 on 2023-09-21 14:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playground', '0004_products_big_brand'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='timetolive',
            field=models.TimeField(default=datetime.time(8, 40, 15)),
        ),
    ]
