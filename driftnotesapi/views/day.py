from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django.http import HttpResponseServerError
from driftnotesapi.models import Day, UserTrip, Trip


class DaySerializer(serializers.ModelSerializer):
    """JSON serializer for Days"""

    class Meta:
        model = Day
        url = serializers.HyperlinkedIdentityField(view_name="day", lookup_field="id")
        fields = ("id", "url", "trip", "date")
        depth = 1


class Days(ViewSet):
    """
    Purpose: Allow a user to communicate with the Drift Notes database to handle Days.
    Methods: GET POST DELETE
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """
        @api {POST} /days POST new day
        @apiName CreateDay
        @apiGroup Day
        """
        try:
            trip_id = request.data.get("trip")
            trip = Trip.objects.get(pk=trip_id)
            user = request.user
            if not UserTrip.objects.filter(user=user, trip=trip).exists():
                raise PermissionDenied("Only a collaborator of the trip can add days!")
            new_day = Day()
            new_day.trip = trip
            new_day.date = request.data["date"]
            new_day.save()

            serializer = DaySerializer(new_day, context={"request": request})

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except KeyError:
            return Response(
                {"message": "Missing required field"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as ex:
            return HttpResponseServerError(ex)

    def retrieve(self, request, pk=None):
        """
        @api {GET} /days/:id GET day matching primary key
        @apiName GetDay
        @apiGroup Day
        """
        user = request.user
        try:
            user_trip = UserTrip.objects.get(user=user)
            day = Day.objects.get(pk=pk, trip=user_trip.trip)
            serializer = DaySerializer(day, context={"request": request})
            return Response(serializer.data)

        except UserTrip.DoesNotExist:
            return Response(
                {"message": "You need to be part of a trip to view this resource."},
                status=status.HTTP_403_FORBIDDEN,
            )
        except Day.DoesNotExist:
            return Response(
                {"message": "This day does not exist. Kinda spooky..."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """
        @api {GET} /days GET all days for all of a user's trips
        @apiName GetDays
        @apiGroup Day
        """
        user = request.user

        try:
            user_trips = UserTrip.objects.filter(user=user)
            trip_ids = user_trips.values_list(
                "trip", flat=True
            )  # shows flat list of trip ids instead of tuples
            # using select_related() method retrieves data in a single query by performing a sql join operation
            days = Day.objects.filter(trip__in=trip_ids).select_related("trip")
            serializer = DaySerializer(days, many=True, context={"request": request})
            return Response(serializer.data)
        except UserTrip.DoesNotExist:
            return Response(
                {"message": "You need to be part of a trip to view this resource."},
                status=status.HTTP_403_FORBIDDEN,
            )
        except Exception as ex:
            return HttpResponseServerError(ex)

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /days/:id DELETE day
        @apiName DeleteDay
        @apiGroup Day

        @apiParam {id} id Day Id to delete
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        try:
            day = Day.objects.get(pk=pk)
            trip = Trip.objects.get(pk=day.trip)
            user = request.user
            if not UserTrip.objects.filter(user=user, trip=trip).exists():
                raise PermissionDenied(
                    "Only a collaborator of the trip can delete days!"
                )
            day.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Day.DoesNotExist:
            return Response(
                {"message": "This day does not exist. Kinda spooky..."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as ex:
            return HttpResponseServerError(ex)
