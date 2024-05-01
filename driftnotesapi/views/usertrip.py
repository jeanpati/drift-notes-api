from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from driftnotesapi.models import UserTrip
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .user import UserSerializer
from .trip import TripSerializer


class UserTripSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for UserTrips"""

    permission_classes = (IsAuthenticatedOrReadOnly,)
    user = UserSerializer(many=False)
    trip = TripSerializer(many=False)

    class Meta:
        model = UserTrip
        url = serializers.HyperlinkedIdentityField(
            view_name="usertrip", lookup_field="id"
        )
        fields = (
            "id",
            "url",
            "user",
            "trip",
        )
        depth = 1


class UserTrips(ViewSet):
    """
    Purpose: Allow a user to communicate with the Drift Notes database to handle UserTrips.
    Methods: GET POST DELETE
    """

    def create(self, request):
        """
        @api {POST} /usertrips POST new usertrip
        @apiName CreateUserTrip
        @apiGroup UserTrip
        """
        try:
            new_usertrip = UserTrip()
            new_usertrip.user = request.data["user"]
            new_usertrip.trip = request.data["trip"]
            new_usertrip.save()

            serializer = UserTripSerializer(new_usertrip, context={"request": request})
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
        @api {GET} /usertrips GET all usertrips
        @apiName GetUserTrips
        @apiGroup UserTrip

        @apiSuccessExample {json} Success
            [
                {
                    "id": 1,
                    "user": 1,
                    "trip": 1
                },
                {
                    "id": 2,
                    "user": 2,
                    "trip": 3
                }
            ]
        """
        try:
            user = request.user
            if user.is_authenticated:
                usertrips = UserTrip.objects.filter(user=user)
            else:
                usertrips = UserTrip.objects.none()

            serializer = UserTripSerializer(
                usertrips, many=True, context={"request": request}
            )
            return Response(serializer.data)

        except Exception as ex:
            return HttpResponseServerError(ex)

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /usertrips/:id DELETE usertrip
        @apiName DeleteUserTrip
        @apiGroup UserTrip
        """
        try:
            usertrip = UserTrip.objects.get(pk=pk)
            usertrip.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except UserTrip.DoesNotExist:
            return Response(
                {"message": "This user trip does not exist. Kinda spooky..."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as ex:
            return HttpResponseServerError(ex)
