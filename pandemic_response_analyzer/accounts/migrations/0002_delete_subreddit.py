# Generated by Django 3.1.4 on 2020-12-29 13:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Subreddit',
        ),
    ]