# Generated by Django 5.0.7 on 2024-07-23 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_alter_product_date_added'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='date_added',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='date_added',
            field=models.DateTimeField(auto_now=True),
        ),
    ]