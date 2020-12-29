from django.db import models

# Create your models here.
class Subreddit(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=500)
    reddit_id = models.CharField(max_length=500)
    created_utc = models.DateTimeField()
    score = models.IntegerField(default=0)
    name = models.CharField(max_length=500)
    upvote_ratio = models.FloatField(default=0.0)

    def __str__(self):
        return self.title