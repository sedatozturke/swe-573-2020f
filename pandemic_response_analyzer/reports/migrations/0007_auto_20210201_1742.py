# Generated by Django 3.1.5 on 2021-02-01 14:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0006_auto_20210201_1735'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reportdetail',
            name='noun_count',
        ),
        migrations.RemoveField(
            model_name='reportdetail',
            name='nouncloud_image_b64',
        ),
    ]
