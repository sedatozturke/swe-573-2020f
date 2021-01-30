from django.db import models
from datasources.models import DataSource

class Crawling(models.Model):
    source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    start_date = models.DateTimeField('date started')

class Subreddit(models.Model):
    created_utc = models.DateTimeField('created date utc')
    subreddit_id = models.CharField(max_length=50)
    subreddit_full_id = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    public_description = models.CharField(max_length=500)
    display_name = models.CharField(max_length=100)
    subscriber_count = models.IntegerField(default=0)

class Submission(models.Model):
    created_utc = models.DateTimeField('created date utc')
    submission_id = models.CharField(max_length=50)
    submission_full_id = models.CharField(max_length=50)
    num_all_comments = models.IntegerField(max_length=50)
    score = models.IntegerField(default=0)
    upvote_ratio = models.FloatField(default=0.0)
    text = models.CharField(max_length=5000)
    title = models.CharField(max_length=500)
    is_self = models.BooleanField(default=False)
    subreddit = models.ForeignKey(Subreddit, on_delete=models.CASCADE)