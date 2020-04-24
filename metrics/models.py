from django.db import models

import datetime

# Create your models here.
class Metric(models.Model):
    """
    models represents performance metrics 
    (impressions, clicks, installs, spend, revenue)
    """

    channel = models.CharField(max_length=100, default="google")
    country = models.CharField(max_length=2, default="DE")
    os = models.CharField(max_length=50, default="ios")
    impressions = models.IntegerField(default=1000)
    clicks = models.IntegerField(default=100)
    installs = models.IntegerField(default=100)
    spend = models.FloatField(default=50.6)
    revenue = models.FloatField(default=50.6)
    date = models.DateField(default=datetime.date.today)

