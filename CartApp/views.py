from Apps.otp import *
from rest_framework import viewsets, status
from Apps.myrenderer import MyRenderer
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from rest_framework.throttling import AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from CartApp.models import Cart
from CartApp.serializers import CartSerializer
from Apps.permissions import IsAdminOrBuyerOnly


# Create your views here.


class CartView(viewsets.ModelViewSet):
    """CartView Only Admin and Buyer can Crud Thier Own Cart"""

    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    renderer_classes = [MyRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrBuyerOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == "admin":
            return Cart.objects.all()
        return Cart.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_superuser and user.role == "author":
            raise PermissionDenied("only buyer have permission to perform cartitem")

        if not user.is_superuser and user.role == "basic_user":
            if hasattr(user, "cart"):
                
                raise PermissionDenied("You already have a cart.")
            serializer.save(user=user)
            return

        if user.is_superuser and user.role == "admin":
            serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()

        if user.role == "author" and not user.is_superuser:
            raise PermissionDenied("Authors cannot update cart items.")

        if user.role == "basic_user" and not user.is_superuser:
            if instance.user != user:
                raise PermissionDenied("You cannot update another user's cart.")
            serializer.save(user=user)
            return

        serializer.save()
