from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryView

app_name = "category"

router = DefaultRouter()
router.register("", CategoryView, basename="category")  # /categories/

urlpatterns = [
    path("", include(router.urls)),
]


# urlpatterns = [
#     path("get/", CategoryView.as_view({"get": "list"}), name="category-list"),
#     path("post/", CategoryView.as_view({"post": "create"}), name="category-create"),
#     path(
#         "retrieve/<str:pk>/",
#         CategoryView.as_view({"get": "retrieve"}),
#         name="category-retrieve",
#     ),
#     path(
#         "update/<str:pk>/",
#         CategoryView.as_view({"put": "update", "patch": "partial_update"}),
#         name="category-update",
#     ),
#     path(
#         "delete/<str:pk>/",
#         CategoryView.as_view({"delete": "destroy"}),
#         name="category-delete",
#     ),
# ]
