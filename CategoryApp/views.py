from Apps.otp import *
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from Apps.filters import BooksFilter, CategoryFilter
from rest_framework.throttling import AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


from CategoryApp.models import Category
from Apps.permissions import IsAdminOrReadOnly
from CategoryApp.serializers import CategorySerializer


# Create your views here.
class CategoryView(viewsets.ModelViewSet):
    """CategoryView Only Admin and  can Crud Category"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CategoryFilter
    search_fields = ["id", "category_name", "origin"]
    ordering_fields = ["id", "category_name", "origin"]

    def list(self, request, *args, **kwargs):
        resp = super().list(request, *args, **kwargs)
        return Response(
            {
                "msg": "Category fetched successfully !",
                "data": resp.data,
                "status": resp.status_code,
            },
            status=resp.status_code,
        )

    def retrieve(self, request, *args, **kwargs):
        resp = super().retrieve(request, *args, **kwargs)
        return Response(
            {
                "msg": "Category retrived successfully !",
                "data": resp.data,
                "status": resp.status_code,
            },
            status=resp.status_code,
        )

    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)  # calls perform_create()
        return Response(
            {
                "msg": "Category created successfully !",
                "data": resp.data,
                "status": resp.status_code,
            },
            status=resp.status_code,
        )

    def update(self, request, *args, **kwargs):
        resp = super().update(request, *args, **kwargs)  # calls perform_update()
        return Response(
            {
                "msg": "Category updated successfully !",
                "data": resp.data,
                "status": resp.status_code,
            },
            status=resp.status_code,
        )

    def partial_update(self, request, *args, **kwargs):
        resp = super().partial_update(
            request, *args, **kwargs
        )  # calls perform_update()
        return Response(
            {
                "msg": "Category updated successfully !",
                "data": resp.data,
                "status": resp.status_code,
            },
            status=resp.status_code,
        )

    def destroy(self, request, *args, **kwargs):
        resp = super().destroy(request, *args, **kwargs)
        return Response(
            {"msg": "Category deleted successfully !", "status": resp.status_code},
            status=status.HTTP_204_NO_CONTENT,
        )
