# Generated by Django 4.2.5 on 2023-09-21 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playground', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=30)),
                ('lastname', models.CharField(max_length=30)),
                ('username', models.CharField(max_length=20)),
                ('password', models.CharField(max_length=30)),
                ('email', models.CharField(max_length=100)),
                ('birthdate', models.DateField()),
                ('favoritecolor', models.CharField(max_length=20, null=True)),
            ],
        ),
    ]