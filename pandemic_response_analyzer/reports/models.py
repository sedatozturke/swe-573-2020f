from django.db import models

# Create your models here.
class Report(models.Model):
    name = models.CharField(max_length=100)
    report_type = models.CharField(max_length=100, default='Instant Report')
    tags = models.CharField(max_length=200)
    status = models.CharField(max_length=50)
    start_date = models.DateTimeField('date started')
    end_date = models.DateTimeField('date ended')

    def __str__(self):
        return self.name
