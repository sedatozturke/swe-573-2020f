# Generated by Django 3.1.6 on 2021-02-02 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0009_reportdetail_graph_image_b64'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportdetail',
            name='graph_image_b64',
            field=models.CharField(max_length=250000, null=True),
        ),
    ]