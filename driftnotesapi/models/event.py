from django.db import models
from datetime import datetime, timedelta


def event_start():
    return datetime.now().time()


def event_end():
    return (datetime.now() + timedelta(hours=2)).time()


class Event(models.Model):
    day = models.ForeignKey("Day", on_delete=models.CASCADE)
    title = models.CharField(max_length=155)
    location = models.CharField(max_length=155, blank=True, null=True)
    start_time = models.TimeField(default=event_start)
    end_time = models.TimeField(default=event_end)
    category = models.ForeignKey(
        "Category", on_delete=models.DO_NOTHING, null=True, blank=True
    )
