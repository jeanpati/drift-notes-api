from django.db import models
from django.contrib.auth.models import User


class Trip(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trips")
    title = models.CharField(max_length=155)
    city = models.CharField(max_length=155)
    start_date = models.DateField(
        default="0000-00-00",
    )
    end_date = models.DateField(
        default="0000-00-00",
    )
