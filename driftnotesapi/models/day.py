from django.db import models


class Day(models.Model):
    trip = models.ForeignKey("Trip", on_delete=models.DO_NOTHING, null=True)
    name = models.CharField(max_length=55)
    date = models.DateField(
        default="0000-00-00",
    )
