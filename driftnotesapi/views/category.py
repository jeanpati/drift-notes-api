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
        """
        @api {POST} /categories POST new category
        @apiName CreateCategory
        @apiGroup Category

        @apiParamExample {json} Input
            {
                "name": "Business"
            }
        """
        try:
            new_category = Category()
            new_category.name = request.data["name"]
            new_category.save()

            serializer = CategorySerializer(new_category, context={"request": request})

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
        @api {GET} /categories/:id GET category matching primary key
        @apiName GetCategory
        @apiGroup Category
        """
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category, context={"request": request})
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response(
                {"message": "This category does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """
        @api {GET} /categories GET all categories
        @apiName GetCategory
        @apiGroup Category
        """
        try:
            categories = Category.objects.all()
            serializer = CategorySerializer(
                categories, many=True, context={"request": request}
            )
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)
