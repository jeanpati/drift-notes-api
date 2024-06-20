from django.db import models
from django.contrib.auth.models import User


class Trip(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trips")
    title = models.CharField(max_length=155)
    city = models.CharField(max_length=155)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    start_date = models.DateField(
        null=True,
    )
    end_date = models.DateField(
        null=True
    )
