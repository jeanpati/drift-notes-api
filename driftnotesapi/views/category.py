from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from driftnotesapi.models import Category
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for product category"""

    class Meta:
        model = Category
        url = serializers.HyperlinkedIdentityField(
            view_name="category", lookup_field="id"
        )
        fields = ("id", "url", "name")


class Categories(ViewSet):
    """Categories for events"""

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized  category instance
        """
        new_category = Category()
        new_category.name = request.data["name"]
        new_category.save()

        serializer = CategorySerializer(new_category, context={"request": request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single category"""
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category, context={"request": request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """Handle GET requests to Category resource"""
        category = Category.objects.all()

        # Support filtering ProductCategorys by area id
        # name = self.request.query_params.get('name', None)
        # if name is not None:
        #     ProductCategories = ProductCategories.filter(name=name)

        serializer = CategorySerializer(
            category, many=True, context={"request": request}
        )
        return Response(serializer.data)
