from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BooksView

app_name = "books"

router = DefaultRouter()


router.register("", BooksView, basename="books")

urlpatterns = [
    path("", include(router.urls)),
]
