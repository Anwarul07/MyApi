from rest_framework import viewsets, status
from rest_framework.response import Response
from Apps.myrenderer import MyRenderer
from django.core.exceptions import PermissionDenied
from Apps.filters import Cartiemfilter
from rest_framework.throttling import AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from Cartitem.models import CartItem
from Cartitem.serializers import CartItemSerializer

from Apps.permissions import IsAdminOrBuyerOnly
from rest_framework.authentication import SessionAuthentication


# Create your views here.


class CartItemView(viewsets.ModelViewSet):
    """CartItmeView Only Admin and Buyer can Crud Thier Own CartItem"""

    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    renderer_classes = [MyRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrBuyerOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = Cartiemfilter
    search_fields = [
        "id",
        "user__username",
        "user__first_name",
        "user__last_name",
        "books__title",
        "books__price",
        "quantity",
    ]
    ordering_fields = [
        "id",
        "user__username",
        "user__first_name",
        "user__last_name",
        "books__title",
        "books__price",
        "quantity",
    ]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == "admin":
            return CartItem.objects.all()
        return CartItem.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_superuser and user.role == "author":
            raise PermissionDenied("only buyer have permission to perform cartitem")

        if not user.is_superuser and user.role == "basic_user":
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

    def get_object(self):
        obj = super().get_object()
        print(obj.user, self.request.user)
        if obj.user != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied("You cannot access another user's cart item")
        return obj
