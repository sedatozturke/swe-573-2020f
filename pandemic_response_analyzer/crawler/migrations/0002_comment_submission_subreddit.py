# Generated by Django 3.1.5 on 2021-01-30 18:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subreddit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subreddit_id', models.CharField(max_length=50, unique=True)),
                ('subreddit_full_id', models.CharField(max_length=50, unique=True)),
                ('description', models.CharField(max_length=500)),
                ('public_description', models.CharField(max_length=500)),
                ('display_name', models.CharField(max_length=100)),
                ('subscriber_count', models.IntegerField(default=0)),
                ('created_utc', models.DateTimeField(verbose_name='created date utc')),
                ('subreddit_created_utc', models.DateTimeField(verbose_name='subreddit created date utc')),
                ('crawling', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='crawler.crawling')),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submission_id', models.CharField(max_length=50, unique=True)),
                ('submission_full_id', models.CharField(max_length=50, unique=True)),
                ('text', models.CharField(max_length=5000)),
                ('title', models.CharField(max_length=500)),
                ('num_all_comments', models.IntegerField(default=0)),
                ('score', models.IntegerField(default=0)),
                ('upvote_ratio', models.FloatField(default=0.0)),
                ('created_utc', models.DateTimeField(verbose_name='created date utc')),
                ('submission_created_utc', models.DateTimeField(verbose_name='submission created date utc')),
                ('crawling', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='crawler.crawling')),
                ('subreddit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crawler.subreddit')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_id', models.CharField(max_length=50, unique=True)),
                ('parent_id', models.CharField(max_length=50)),
                ('comment_subreddit_id', models.CharField(max_length=50)),
                ('score', models.IntegerField(default=0)),
                ('body', models.CharField(max_length=5000)),
                ('created_utc', models.DateTimeField(verbose_name='created date utc')),
                ('comment_created_utc', models.DateTimeField(verbose_name='comment created date utc')),
                ('crawling', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='crawler.crawling')),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crawler.submission')),
                ('subreddit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crawler.subreddit')),
            ],
        ),
    ]