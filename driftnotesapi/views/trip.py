from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from driftnotesapi.models import Trip, UserTrip
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied


class TripSerializer(serializers.ModelSerializer):
    """JSON serializer for trips"""

    class Meta:
        model = Trip
        url = serializers.HyperlinkedIdentityField(view_name="trip", lookup_field="id")
        fields = (
            "id",
            "url",
            "title",
            "city",
            "start_date",
            "end_date",
        )
        depth = 1


class Trips(ViewSet):
    """Request handlers for Trips in the Drift Notes platform"""

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """
        @api {POST} /trips POST new trip
        @apiName CreateTrip
        @apiGroup Trip

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {String} title Name of the trip
        @apiParam {String} city Destination for the trip
        @apiParam {Date} start_date Start date of the trip (YYYY-MM-DD)
        @apiParam {Date} end_date End date of the trip (YYYY-MM-DD)

        @apiParamExample {json} Input
            {
                "title": "My Trip",
                "city": "New York",
                "start_date": "2024-05-01",
                "end_date": "2024-05-10"
            }

        @apiSuccessExample {json} Success
            {
                "id": 1,
                "title": "My Trip",
                "city": "New York",
                "start_date": "2024-05-01",
                "end_date": "2024-05-10"
            }
        """

        new_trip = Trip()
        new_trip.creator = request.user
        new_trip.title = request.data["title"]
        new_trip.city = request.data["city"]
        new_trip.start_date = request.data["start_date"]
        new_trip.end_date = request.data["end_date"]
        new_trip.save()

        UserTrip.objects.create(user=new_trip.creator, trip=new_trip)

        serializer = TripSerializer(new_trip, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        """
        @api {GET} /trips GET all trips
        @apiName GetTrips
        @apiGroup Trip
        """
        user = request.user
        if user.is_authenticated:
            trip_ids = UserTrip.objects.filter(user=user).values_list(
                "trip_id", flat=True
            )
            trips = Trip.objects.filter(id__in=trip_ids)
        else:
            trips = Trip.objects.none()

        serializer = TripSerializer(trips, many=True, context={"request": request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        @api {GET} /stores/:id GET store matching primary key
        @apiName GetStore
        @apiGroup Store
        """
        try:
            trip = Trip.objects.get(pk=pk)
            serializer = TripSerializer(trip, context={"request": request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """
        @api {PUT} /trips/:id PUT edit trip data
        @apiName EditTrip
        @apiGroup Trip
        """
        try:
            trip = Trip.objects.get(pk=pk)
        except Trip.DoesNotExist:
            return Response(
                {"message": "This trip does not exist o.o"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the user is the owner of the trip
        if trip.seller.user != request.auth.user:
            raise PermissionDenied("Smile! You're on camera! This is not your trip!")

        # Update trip data based on request data
        # If the key "name" exists in the request.data, its value is returned.
        # If not, it returns the default value, which is trip.name.
        trip.name = request.data.get("name", trip.name)
        trip.description = request.data.get("description", trip.description)
        trip.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /trips/:id DELETE trip matching id
        @apiName RemoveTrip
        @apiGroup Trip
        """
        try:
            # Check if the user is the owner of the trip
            trip = Trip.objects.get(pk=pk)
            if trip.creator != request.auth.user:
                raise PermissionDenied(
                    "Smile! You're on camera! This is not your trip!"
                )
            trip.delete()

            return Response(
                "Your trip was successfully destroyed!",
                status=status.HTTP_204_NO_CONTENT,
            )

        except Trip.DoesNotExist as ex:
            return Response(
                {"This trip does not exist. Kinda spooky...": ex.args[0]},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as ex:
            return Response(
                {"An unexpected error occurred. Uh oh.": ex.args[0]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
