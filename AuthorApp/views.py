from Apps.otp import *
from rest_framework import viewsets
from rest_framework import viewsets, status
from Apps.myrenderer import MyRenderer
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from Apps.filters import BooksFilter, CategoryFilter
from rest_framework.throttling import AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from AuthorApp.models import Author
from Apps.filters import AuthorFilter
from AuthorApp.serializers import AuthorSerializer
from Apps.permissions import (
    IsAdminOrAuthorSpecificOrReadOnly,
    IsAdminOrAuthorOnly,
)

from django.shortcuts import render

# Create your views here.


class AuthorView(viewsets.ModelViewSet):
    """AuthorView Only Admin and Author can Crud Thier Own profile"""

    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    renderer_classes = [MyRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrAuthorSpecificOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AuthorFilter
    search_fields = [
        "id",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "user__mobile",
    ]
    ordering_fields = [
        "id",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "user__mobile",
    ]

    def perform_create(self, serializer):
        users = self.request.user

        if users.is_authenticated and not users.is_superuser:
            raise PermissionDenied(
                "You are already logged in. You cannot register another user."
            )
        if users.role == "author":
            serializer.save(is_verified=False, user=users)
        else:
            serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        author = self.get_object()

        # AUTHOR cannot self-verify
        if user.role == "author":
            serializer.save(is_verified=author.is_verified)
            return

        # ADMIN can verify / reject
        if user.is_superuser or user.role == "admin":
            serializer.save()
            return

        raise PermissionDenied("You are not allowed to update this profile.")


class AuthorOnlyView(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    renderer_classes = [MyRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrAuthorOnly]

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Author.objects.none()

        if user.is_superuser or user.role == "admin":
            return Author.objects.all()

        if user.role == "author":
            return Author.objects.filter(user=user)

        return Author.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.is_authenticated and not user.is_superuser:
            raise PermissionDenied(
                "You are already logged in. You cannot register another user."
            )
        if user.role == "author":
            serializer.save(user=user, is_verified=False)
        else:

            serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        author = self.get_object()

        # AUTHOR cannot self-verify
        if user.role == "author":
            serializer.save(is_verified=author.is_verified)
            return

        # ADMIN can verify / reject
        if user.is_superuser or user.role == "admin":
            serializer.save()
            return

        raise PermissionDenied("You are not allowed to update this profile.")
