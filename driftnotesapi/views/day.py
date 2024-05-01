from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django.http import HttpResponseServerError
from driftnotesapi.models import Day, UserTrip


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
    Methods: GET PUT POST DELETE
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """
        @api {POST} /days POST new day
        @apiName CreateDay
        @apiGroup Day
        """
        try:
            new_day = Day()
            new_day.trip = request.data["trip"]
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
        try:
            day = Day.objects.get(pk=pk)
            serializer = DaySerializer(day, context={"request": request})
            return Response(serializer.data)
        except Day.DoesNotExist:
            return Response(
                {"message": "This day does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """
        @api {GET} /days GET all days
        @apiName GetDays
        @apiGroup Day
        """
        user = request.user
        try:
            user_trip = UserTrip.objects.get(user=user)
        except UserTrip.DoesNotExist:
            return Response(
                {"message": "You need to be part of a trip to view this resource."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            days = Day.objects.filter(trip=user_trip.trip)
            serializer = DaySerializer(days, many=True, context={"request": request})
            return Response(serializer.data)
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
            day.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Day.DoesNotExist:
            return Response(
                {"message": "Day not found"}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception as ex:
            return HttpResponseServerError(ex)
