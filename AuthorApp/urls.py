from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthorView, AuthorOnlyView

app_name = "author"

router = DefaultRouter()


router.register("all", AuthorView, basename="author")
router.register("profile", AuthorOnlyView, basename="profile")

urlpatterns = [
    path("", include(router.urls)),
]
