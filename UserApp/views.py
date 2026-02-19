from Apps.otp import *
from rest_framework import viewsets
from rest_framework import generics, status
from rest_framework.response import Response
from Apps.myrenderer import MyRenderer
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from django.core.exceptions import PermissionDenied
from Apps.filters import BooksFilter, CategoryFilter
from rest_framework.throttling import AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from UserApp.models import CustomUser
from Apps.filters import UserFilters
from UserApp.serializers import UserSerializer
from Apps.serializers import (
    VerifyOTPAndRegisterSerializer,
    VerifyOTPAndUpdatePasswordSerializer,
)

from Apps.permissions import IsAdminOrAuthorOrBuyerOnly, IsAdminOrAnonymousOnly

# Create your views here.


class UserView(viewsets.ModelViewSet):
    """UserView Only Admin and User can  Thier Own profile"""

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    renderer_classes = [MyRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrAuthorOrBuyerOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserFilters
    search_fields = [
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "mobile",
    ]
    ordering_fields = [
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "mobile",
    ]

    def get_serializer_class(self):
        request = self.request
        user = request.user
        if self.request.method == "POST":
            if self.request.user.is_authenticated and self.request.user.is_superuser:
                return UserSerializer
            return VerifyOTPAndRegisterSerializer

        if self.request.method in ["PUT", "PATCH"]:
            # Admin → direct serializer
            if user.is_superuser or user.role == CustomUser.ADMIN:
                return UserSerializer

            # Non-admin password update → OTP serializer
            if "password" in request.data:
                return VerifyOTPAndUpdatePasswordSerializer

            # Non-admin profile update
            return UserSerializer

        return UserSerializer

    def perform_create(self, serializer):
        user = self.request.user

        #  Non-admin logged in  cannot create another  users
        if user.is_authenticated and not user.is_superuser:
            raise PermissionDenied(
                "You are already logged in. You cannot register another user."
            )

        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        target = self.get_object()

        if user.is_superuser or user.role == "admin":
            serializer.save()
            return

        #  ---------- AUTHOR / BASIC USER (SELF ONLY) ----------
        if user.id == target.id:
            serializer.save(
                role=target.role,
                is_superuser=target.is_superuser,
                is_staff=target.is_staff,
            )
            return

        raise PermissionDenied("You are not allowed to update this user.")

    def get_queryset(self):
        user = self.request.user

        # if self.request.method == "POST":
        #     return CustomUser.objects.none()

        if not user.is_authenticated:
            return CustomUser.objects.none()

        if user.is_superuser or user.role == CustomUser.ADMIN:
            return CustomUser.objects.all()

        return CustomUser.objects.filter(id=user.id)
