# Generated by Django 3.1.5 on 2021-02-01 14:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0005_auto_20210201_1259'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportdetail',
            name='noun_count',
            field=models.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='reportdetail',
            name='nouncloud_image_b64',
            field=models.CharField(max_length=100000, null=True),
        ),
        migrations.AlterField(
            model_name='reportdetail',
            name='report',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='reports.report'),
        ),
        migrations.AlterField(
            model_name='reportdetail',
            name='word_count',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='reportdetail',
            name='wordcloud_image_b64',
            field=models.CharField(max_length=100000, null=True),
        ),
    ]
