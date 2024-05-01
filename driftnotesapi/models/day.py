from django.db import models


class Day(models.Model):
    trip = models.ForeignKey("Trip", on_delete=models.CASCADE)
    date = models.DateField(
        default="0000-00-00",
    )
