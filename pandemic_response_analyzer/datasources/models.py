from django.db import models

# Create your models here.
class DataSource(models.Model):
    platform = models.CharField(max_length=10)
    tag = models.CharField(max_length=200)
    source_type = models.CharField(max_length=50)
    source_key = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    weight = models.IntegerField(default=1)

    def __str__(self):
        return self.source_key