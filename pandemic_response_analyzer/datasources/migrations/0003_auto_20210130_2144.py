# Generated by Django 3.1.5 on 2021-01-30 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasources', '0002_auto_20210130_0348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasource',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
