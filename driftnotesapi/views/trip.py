from django.http import HttpResponseServerError, HttpResponse
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from driftnotesapi.models import Trip, UserTrip
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied
from .user import UserSerializer


class TripSerializer(serializers.ModelSerializer):
    """JSON serializer for trips"""

    creator = UserSerializer(many=False)

    class Meta:
        model = Trip
        url = serializers.HyperlinkedIdentityField(view_name="trip", lookup_field="id")
        fields = (
            "id",
            "url",
            "creator",
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

        try:
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
        except KeyError:
            return Response(
                {"message": "Missing required field"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """
        @api {GET} /trips GET all trips
        @apiName GetTrips
        @apiGroup Trip
        """
        user = request.user
        if user.is_authenticated:
            try:
                all_trips = Trip.objects.all()
                serializer = TripSerializer(
                    all_trips, context={"request": request}, many=True
                )
                return Response(serializer.data)
            except Exception as ex:
                return HttpResponseServerError(ex)
        else:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    def retrieve(self, request, pk=None):
        """
        @api {GET} /trips/:id GET trips matching primary key
        @apiName GetTrip
        @apiGroup Trip
        """
        user = request.user
        if user.is_authenticated:
            try:
                trip = Trip.objects.get(pk=pk)
                serializer = TripSerializer(trip, context={"request": request})
                return Response(serializer.data)
            except Trip.DoesNotExist:
                return Response(
                    {"message": "This trip does not exist. Kinda spooky..."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except Exception as ex:
                return HttpResponseServerError(ex)
        else:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

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
                {"message": "This trip does not exist. Kinda spooky..."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the user is the owner of the trip
        if trip.seller.user != request.auth.user:
            raise PermissionDenied("Only the creator of the trip can edit it!")

        # Update trip data based on request data
        # If the key "name" exists in the request.data, its value is returned.
        # If not, it returns the default value, which is trip.name.
        trip.title = request.data.get("title", trip.title)
        trip.city = request.data.get("city", trip.city)
        trip.start_date = request.data.get("start_date", trip.start_date)
        trip.end_date = request.data.get("end_date", trip.end_date)
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
                raise PermissionDenied("Only the creator of the trip can delete it!")
            trip.delete()

            return Response(
                "Your trip was successfully destroyed!",
                status=status.HTTP_204_NO_CONTENT,
            )

        except Trip.DoesNotExist:
            return Response(
                {"message": "This trip does not exist. Kinda spooky..."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as ex:
            return HttpResponseServerError(ex)
