from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from driftnotesapi.models import *
from driftnotesapi.views import *

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"users", Users, "user")
router.register(r"categories", Categories, "category")
router.register(r"trips", Trips, "trip")
router.register(r"usertrips", UserTrips, "usertrip")
router.register(r"days", Days, "day")
router.register(r"events", Events, "event")


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("register", register_user),
    path("login", login_user),
    path("api-token-auth", obtain_auth_token),
    path("api-auth", include("rest_framework.urls", namespace="rest_framework")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
