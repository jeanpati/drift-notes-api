from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from django.contrib.auth.models import User
from rest_framework.exceptions import PermissionDenied


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for Users

    Arguments:
        serializers
    """

    class Meta:
        model = User
        url = serializers.HyperlinkedIdentityField(view_name="user", lookup_field="id")
        fields = (
            "id",
            "url",
            "username",
            "first_name",
            "last_name",
            "email",
        )


class Users(ViewSet):
    """Users for Drift Notes
    Purpose: Allow a user to communicate with the Drift Notes database to GET and PUT Users.
    Methods: GET PUT(id)
    """

    def retrieve(self, request, pk=None):
        """Handle GET requests for single user
        Purpose: Allow a user to communicate with the Drift Notes database to retrieve one user
        Methods:  GET
        Returns:
            Response -- JSON serialized customer instance
        """
        try:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user, context={"request": request})
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """Handle GET requests to user resource"""
        try:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True, context={"request": request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """
        @api {PUT} /users/:id PUT edit user data
        @apiName EditUser
        @apiGroup User
        """
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"message": "This user does not exist. Kinda spooky..."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the user is the owner of the account
        if user != request.user:
            raise PermissionDenied("You do not have permission to edit this user!")

        # Update user data based on request data
        user.username = request.data.get("username", user.username)
        user.first_name = request.data.get("first_name", user.first_name)
        user.last_name = request.data.get("last_name", user.last_name)
        user.password = request.data.get("password", user.password)
        user.email = request.data.get("email", user.email)
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
