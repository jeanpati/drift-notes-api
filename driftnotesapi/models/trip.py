from django.db import models


class Trip(models.Model):
    title = models.CharField(max_length=155)
    city = models.CharField(max_length=155)
    start_date = models.DateField(
        default="0000-00-00",
    )
    end_date = models.DateField(
        default="0000-00-00",
    )
