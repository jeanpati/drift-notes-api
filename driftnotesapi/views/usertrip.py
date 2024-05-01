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
    """JSON serializer for UserTrips

    Arguments:
        serializers
    """

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
    """Users for Drift Notes
    Purpose: Allow a user to communicate with the Drift Notes database to GET PUT POST and DELETE Users.
    Methods: GET PUT(id) POST
    """

    def create(self, request):
        new_usertrip = UserTrip()
        new_usertrip.user = request.data["user"]
        new_usertrip.trip = request.data["trip"]
        new_usertrip.save()

        serializer = UserTripSerializer(new_usertrip, context={"request": request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        """Handle GET requests to usertrips resource"""
        user = request.user
        if user.is_authenticated:
            usertrips = UserTrip.objects.filter(user=user)
        else:
            usertrips = UserTrip.objects.none()

        serializer = UserTripSerializer(
            usertrips, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /products/:id DELETE product
        @apiName DeleteProduct
        @apiGroup Product

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} id Product Id to delete
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        try:
            usertrip = UserTrip.objects.get(pk=pk)
            usertrip.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except UserTrip.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response(
                {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
