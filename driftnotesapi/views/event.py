from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django.http import HttpResponseServerError
from driftnotesapi.models import Event, UserTrip, Day, Category, event_start, event_end
from .day import DaySerializer
from .category import CategorySerializer


class EventSerializer(serializers.ModelSerializer):
    """JSON serializer for Events"""

    day = DaySerializer(many=False)
    category = CategorySerializer(many=False)

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
            day_id = request.data.get("day")
            day = Day.objects.get(pk=day_id)
            trip = day.trip
            user = request.user
            if not UserTrip.objects.filter(user=user, trip=trip).exists():
                raise PermissionDenied(
                    "Only a collaborator of the trip can add events!"
                )
            new_event = Event()
            new_event.day = day
            new_event.title = request.data["title"]
            new_event.location = request.data.get("location", "")
            new_event.start_time = request.data.get("start_time", event_start())
            new_event.end_time = request.data.get("end_time", event_end())
            category_id = request.data.get("category")
            if category_id:
                new_event.category = Category.objects.get(pk=category_id)
            new_event.save()

            serializer = EventSerializer(new_event, context={"request": request})

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except KeyError:
            return Response(
                {"message": "Missing required field"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Day.DoesNotExist:
            return Response(
                {"message": "This day does not exist. Kinda spooky..."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as ex:
            return HttpResponseServerError(ex)

    def retrieve(self, request, pk=None):
        """
        @api {GET} /events/:id GET event matching primary key of a user's trip
        @apiName GetEvent
        @apiGroup Event
        """
        user = request.user
        try:
            user_trip = UserTrip.objects.get(user=user, trip__day__event__pk=pk)
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
                {"message": "This event does not exist. Kinda spooky..."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """
        @api {GET} /events GET all events of a user's trips
        @apiName GetEvents
        @apiGroup Event
        """
        user = request.user
        try:
            user_trips = UserTrip.objects.filter(
                user=user
            )  # gets all UserTrip instances associated with the user
            trip_ids = user_trips.values_list(
                "trip", flat=True
            )  # shows flat list of all trip ids (instead of tuples) associated with the user
            # using select_related() method retrieves data in a single query by performing a sql join operation
            events = Event.objects.filter(day__trip__in=trip_ids).select_related(
                "day__trip"
            )  # fetches all events where it's day belongs to any of the user's trips
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
            return HttpResponseServerError(ex)

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

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Event.DoesNotExist:
            return Response(
                {"message": "This day does not exist. Kinda spooky..."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """
        @api {PUT} /events/:id UPDATE an existing event
        @apiName UpdateEvent
        @apiGroup Event

        @apiParam {id} id Event Id to update
        """
        try:
            event = Event.objects.get(pk=pk)
            user = request.user

            if not UserTrip.objects.filter(user=user, trip=event.day.trip).exists():
                raise PermissionDenied(
                    "Only a collaborator of the trip can update events!"
                )

            day_id = request.data.get("day")
            if day_id:
                # Check if the day belongs to a trip that the user is a part of
                if not UserTrip.objects.filter(
                    user=user, trip__day__pk=day_id
                ).exists():
                    raise PermissionDenied(
                        "You can only add events to days of your trip!"
                    )
                event.day = Day.objects.get(pk=day_id)
            event.title = request.data.get("title", event.title)
            event.location = request.data.get("location", event.location)
            event.start_time = request.data.get("start_time", event.start_time)
            event.end_time = request.data.get("end_time", event.end_time)
            category_id = request.data.get("category")
            if category_id:
                event.category = Category.objects.get(pk=category_id)

            event.save()
            serializer = EventSerializer(event, context={"request": request})
            return Response(serializer.data)

        except Event.DoesNotExist:
            return Response(
                {"message": "This event does not exist. Kinda spooky..."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Day.DoesNotExist:
            return Response(
                {"message": "This day does not exist. Kinda spooky..."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as ex:
            return HttpResponseServerError(ex)
