# Generated by Django 3.1.5 on 2021-02-01 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasources', '0004_auto_20210201_1756'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasource',
            name='collected',
            field=models.BooleanField(default=False),
        ),
    ]
