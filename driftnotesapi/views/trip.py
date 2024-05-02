from django.http import HttpResponseServerError, HttpResponse
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from driftnotesapi.models import Trip, UserTrip, Day
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied
from .user import UserSerializer
from datetime import timedelta, datetime


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
    """
    Purpose: Allow a user to communicate with the Drift Notes database to handle Trips.
    Methods: GET PUT POST DELETE
    """

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

            # Automatically create days for the trip
            # Creates a day instance for each day of the trip starting from the start date
            start_date = new_trip.start_date
            end_date = new_trip.end_date
            while start_date <= end_date:
                Day.objects.create(trip=new_trip, date=start_date)
                start_date += timedelta(days=1)

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

        def parse_date(date_string, default_date=None):
            # Use strptime (string parse time) to convert a date string to a datetime object
            if date_string:
                return datetime.strptime(date_string, "%Y-%m-%d").date()
            else:
                return default_date

        try:
            trip = Trip.objects.get(pk=pk)
        except Trip.DoesNotExist:
            return Response(
                {"message": "This trip does not exist. Kinda spooky..."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the user is a collaborator on the trip
        user = request.user
        if not UserTrip.objects.filter(user=user, trip=trip).exists():
            raise PermissionDenied("Only a collaborator of the trip can edit it!")

        # Update trip data based on request data
        # If the key "name" exists in the request.data, its value is returned.
        # If not, it returns the default value, which is trip.name.
        trip.title = request.data.get("title", trip.title)
        trip.city = request.data.get("city", trip.city)
        trip.start_date = parse_date(request.data.get("start_date", trip.start_date))
        trip.end_date = parse_date(request.data.get("end_date", trip.end_date))
        trip.save()
        # Update days for the trip
        if "start_date" in request.data or "end_date" in request.data:
            # Delete days "less than" or before the new start date
            # Delete days "greater than" or after the new end date
            Day.objects.filter(trip=trip, date__lt=trip.start_date).delete()
            Day.objects.filter(trip=trip, date__gt=trip.end_date).delete()

            # Retrieve the existing days of the trip
            existing_dates = Day.objects.filter(trip=trip).values_list(
                "date", flat=True
            )
            # Calculate the number of days in the trip
            trip_length = (trip.end_date - trip.start_date).days + 1
            # Create a list of dates by incrementally adding the length of the trip to start date
            trip_dates = [
                trip.start_date + timedelta(days=x) for x in range(trip_length)
            ]
            # Turn both lists into sets so we can subtract them
            # Create set of missing dates by subtracting existing_dates from trip_dates
            missing_dates = set(trip_dates) - set(existing_dates)
            # Create instances of Day for each missing date
            for date in missing_dates:
                Day.objects.create(trip=trip, date=date)

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
