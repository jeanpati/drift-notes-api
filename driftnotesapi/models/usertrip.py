from django.db import models
from django.contrib.auth.models import User


class UserTrip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usertrips")
    trip = models.ForeignKey("Trip", on_delete=models.CASCADE, related_name="usertrips")
