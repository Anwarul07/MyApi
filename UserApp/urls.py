from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserView

app_name = "users"

router = DefaultRouter()
router.register("", UserView, basename="user")  

urlpatterns = [
    path("", include(router.urls)),
]
