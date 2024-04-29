from django.db import models


class UserTrip(models.Model):

    user = models.ForeignKey(
        "User", on_delete=models.DO_NOTHING, related_name="usertrips"
    )

    trip = models.ForeignKey(
        "Trip", on_delete=models.DO_NOTHING, related_name="usertrips"
    )
