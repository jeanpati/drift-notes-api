from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django.http import HttpResponseServerError
from driftnotesapi.models import Event, UserTrip, Day


class EventSerializer(serializers.ModelSerializer):
    """JSON serializer for Events"""

    class Meta:
        model = Event
        url = serializers.HyperlinkedIdentityField(view_name="event", lookup_field="id")
        fields = (
            "id",
            "url",
            "day",
            "title",
            "location",
            "start_time",
            "end_time",
            "category",
        )
        depth = 1


class Events(ViewSet):
    """
    Purpose: Allow a user to communicate with the Drift Notes database to handle Events.
    Methods: GET POST DELETE
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """
        @api {POST} /events POST new event
        @apiName CreateEvent
        @apiGroup Event
        """
        try:
            trip_id = request.data.get("trip")
            trip = Day.objects.get(pk=trip_id).trip
            user = request.user

            if not UserTrip.objects.filter(user=user, trip=trip).exists():
                raise PermissionDenied(
                    "Only a collaborator of the trip can add events!"
                )

            new_event = Event()
            new_event.day_id = trip_id
            new_event.title = request.data.get("title")
            new_event.location = request.data.get("location")
            new_event.start_time = request.data.get("start_time")
            new_event.end_time = request.data.get("end_time")
            new_event.category_id = request.data.get("category")
            new_event.save()

            serializer = EventSerializer(new_event, context={"request": request})

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except KeyError as ex:
            return Response(
                {"message": f"Missing required field: {str(ex)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Day.DoesNotExist:
            return Response(
                {"message": "Day not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as ex:
            return HttpResponseServerError({"message": str(ex)})

    def retrieve(self, request, pk=None):
        """
        @api {GET} /events/:id GET event matching primary key
        @apiName GetEvent
        @apiGroup Event
        """
        user = request.user
        try:
            user_trip = UserTrip.objects.get(user=user)
            event = Event.objects.get(pk=pk, day__trip=user_trip.trip)
            serializer = EventSerializer(event, context={"request": request})
            return Response(serializer.data)

        except UserTrip.DoesNotExist:
            return Response(
                {"message": "You need to be part of a trip to view this resource."},
                status=status.HTTP_403_FORBIDDEN,
            )
        except Event.DoesNotExist:
            return Response(
                {"message": "This event does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as ex:
            return HttpResponseServerError({"message": str(ex)})

    def list(self, request):
        """
        @api {GET} /events GET all events
        @apiName GetEvents
        @apiGroup Event
        """
        user = request.user

        try:
            user_trips = UserTrip.objects.filter(user=user)
            trip_ids = user_trips.values_list(
                "trip", flat=True
            )  # shows flat list of trip ids instead of tuples
            events = Event.objects.filter(day__trip__in=trip_ids)
            serializer = EventSerializer(
                events, many=True, context={"request": request}
            )
            return Response(serializer.data)
        except UserTrip.DoesNotExist:
            return Response(
                {"message": "You need to be part of a trip to view this resource."},
                status=status.HTTP_403_FORBIDDEN,
            )
        except Exception as ex:
            return HttpResponseServerError({"message": str(ex)})

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /events/:id DELETE event
        @apiName DeleteEvent
        @apiGroup Event

        @apiParam {id} id Event Id to delete
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        try:
            event = Event.objects.get(pk=pk)
            user = request.user

            if not UserTrip.objects.filter(user=user, trip=event.day.trip).exists():
                raise PermissionDenied(
                    "Only a collaborator of the trip can delete events!"
                )
            event.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Event.DoesNotExist:
            return Response(
                {"message": "Event not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as ex:
            return HttpResponseServerError({"message": str(ex)})
