from django.db import models
from datasources.models import DataSource
class Crawling(models.Model):
    source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    start_date = models.DateTimeField('date started')

class Subreddit(models.Model):
    subreddit_id = models.CharField(max_length=50, unique=True)
    subreddit_full_id = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=500)
    public_description = models.CharField(max_length=500)
    display_name = models.CharField(max_length=100)
    subscriber_count = models.IntegerField(default=0)
    created_utc = models.DateTimeField('created date utc')
    subreddit_created_utc = models.DateTimeField('subreddit created date utc')
    crawling=models.ForeignKey(Crawling, on_delete=models.CASCADE, null=True)

class Submission(models.Model):
    submission_id = models.CharField(max_length=50, unique=True)
    submission_full_id = models.CharField(max_length=50, unique=True)
    text = models.CharField(max_length=5000)
    title = models.CharField(max_length=500)
    num_all_comments = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    upvote_ratio = models.FloatField(default=0.0)
    subreddit = models.ForeignKey(Subreddit, on_delete=models.CASCADE)
    created_utc = models.DateTimeField('created date utc')
    submission_created_utc = models.DateTimeField('submission created date utc')
    crawling=models.ForeignKey(Crawling, on_delete=models.CASCADE, null=True)

class Comment(models.Model):
    comment_id = models.CharField(max_length=50, unique=True)
    parent_id = models.CharField(max_length=50)
    comment_subreddit_id = models.CharField(max_length=50)
    score = models.IntegerField(default=0)
    body = models.CharField(max_length=10000)
    subreddit = models.ForeignKey(Subreddit, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    created_utc = models.DateTimeField('created date utc')
    comment_created_utc = models.DateTimeField('comment created date utc')
    crawling=models.ForeignKey(Crawling, on_delete=models.CASCADE, null=True)