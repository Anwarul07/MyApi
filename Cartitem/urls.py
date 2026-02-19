from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartItemView

app_name = "cartitem"

router = DefaultRouter()
router.register("", CartItemView, basename="cartitem")

urlpatterns = [
    path("", include(router.urls)),
]
