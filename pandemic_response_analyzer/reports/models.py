from django.db import models
from crawler.models import Submission, Subreddit, Comment

# Create your models here.
class Report(models.Model):
    name = models.CharField(max_length=100)
    report_type = models.CharField(max_length=100, default='Instant Report')
    tags = models.CharField(max_length=200)
    status = models.CharField(max_length=50, default='Started')
    start_date = models.DateTimeField('date started')
    end_date = models.DateTimeField('date ended')

    def __str__(self):
        return self.name

class ReportDetail(models.Model):
    report = models.OneToOneField(Report, on_delete=models.CASCADE)
    wordcloud_image_b64 = models.CharField(max_length=100000, null=True)
    word_count = models.JSONField(null=True)


class SubmissionReport(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    title_polarity = models.FloatField(default=0.0)
    title_subjectivity = models.FloatField(default=0.0)
    title_sentiment = models.CharField(default='Neutral', max_length=20)
    text_polarity = models.FloatField(default=0.0)
    text_subjectivity = models.FloatField(default=0.0)
    text_sentiment = models.CharField(default='Neutral', max_length=20)

class CommentReport(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    body_polarity = models.FloatField(default=0.0)
    body_subjectivity = models.FloatField(default=0.0)
    body_sentiment = models.CharField(default='Neutral', max_length=20)


