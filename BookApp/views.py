from Apps.otp import *
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from Apps.myrenderer import MyRenderer
from Apps.filters import BooksFilter, CategoryFilter
from rest_framework.throttling import AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from BookApp.models import Books
from BookApp.serializers import BooksSerializer
from Apps.permissions import IsAdminOrAuthorOrReadOnly


# Create your views here.
class BooksView(viewsets.ModelViewSet):
    """BookView Only Admin and Author can Crud Thier Books"""

    queryset = Books.objects.all()
    serializer_class = BooksSerializer
    renderer_classes = [MyRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BooksFilter
    search_fields = [
        "title",
        "category__category_name",
        "author__user__username",
        "isbn",
    ]
    ordering_fields = [
        "id",
        "price",
        "publication_date",
        "title",
        "category__category_name",
        "author__user__username",
    ]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == "author":
            if not user.author_profile.is_verified:
                raise PermissionDenied(
                    "You are not verified. Verified authors only can create books."
                )
            serializer.save(
                author=user.author_profile,
                availability="pending",
            )
        else:
            serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        book = self.get_object()
        if user.role == "author":
            if not user.author_profile.is_verified:
                raise PermissionDenied(
                    "You are not verified. Verified authors only can update books."
                )
            serializer.save(
                author=user.author_profile,
                availability=book.availability,
            )
        else:
            serializer.save()
