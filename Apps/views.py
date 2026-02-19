from Apps.otp import *
from rest_framework import viewsets
from django.http import JsonResponse
from rest_framework.reverse import reverse
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from django.core.exceptions import PermissionDenied
from Apps.filters import BooksFilter, CategoryFilter
from rest_framework.throttling import AnonRateThrottle
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()

from BookApp.models import Books
from AuthorApp.models import Author
from CategoryApp.models import Category
from Apps.serializers import (
    SendOTPSerializer,
    VerifyOTPAndRegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
    LogoutAllSerializer,
    SendLoginOTPSerializer,
    SendPasswordUpdateOTPSerializer,
    VerifyOTPAndUpdatePasswordSerializer,
    VerifyOTPAndResetPasswordSerializer,
    SendForgetPasswordOTPSerializer,
    SendUserDeleteOTPSerializer,
    VerifyOTPAndDeleteUserSerializer,
)

from Apps.permissions import IsAdminOrAnonymousOnly


# OTP Views


# ---------------Register Otp View for User Registration -------------
class SendOTPView(generics.CreateAPIView):
    http_method_names = ["post"]
    serializer_class = SendOTPSerializer
    throttle_classes = [AnonRateThrottle]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrAnonymousOnly]

    def create(self, request, *args, **kwargs):
        user = self.request.user

        if user.is_authenticated and not user.is_superuser:
            raise PermissionDenied(
                "You are already logged in. You cannot register another user."
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp_via = serializer.validated_data.get("otp_via")
        email = serializer.validated_data.get("email")
        mobile = serializer.validated_data.get("mobile")

        otp_obj = serializer.save()
        return Response(
            {
                "message": "OTP sent successfully via {}".format(otp_via),
                "email": otp_obj.email,
                "mobile": otp_obj.mobile,
                "send_time": otp_obj.created_at,
                "expires_at": otp_obj.expires_at,
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


# ---------------Register Confirm View for User Registration -------------
class UserRegisterView(generics.CreateAPIView):
    http_method_names = ["post"]
    serializer_class = VerifyOTPAndRegisterSerializer
    authentication_classes = []
    permission_classes = [IsAdminOrAnonymousOnly]

    def create(self, request, *args, **kwargs):
        user = self.request.user

        if user.is_authenticated and not user.is_superuser:
            raise PermissionDenied(
                "You are already logged in. You cannot register another user."
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created_user = serializer.save()
        return Response(
            {
                "message": "User registered successfully",
                "user_id": created_user.id,
                "email": created_user.email,
                "mobile": created_user.mobile,
                "role": created_user.role,
                "status": status.HTTP_201_CREATED,
            },
            status=status.HTTP_201_CREATED,
        )


# ---------------Login Otp View for User Login -------------
class SendLoginOTPView(generics.CreateAPIView):
    """
    Send OTP for login via Email or Mobile
    """

    serializer_class = SendLoginOTPSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.save()

        return Response(
            {
                "otp_via": otp.otp_via,
                "message": f"OTP sent successfully for {otp.otp_via} login.",
                "email": otp.email,
                "mobile": otp.mobile,
                "expires_at": otp.expires_at,
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


# ---------------Login Confirm  View for User Login -------------
class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(
            {
                "msg": "Login Successfully",
                "data": data,
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


# ---------------Logout  View for User Logout -------------
class LogoutView(generics.CreateAPIView):
    serializer_class = LogoutSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "message": "Logged out successfully",
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


# ---------------Logout All Devices  View for User Logout -------------
class LogoutAllView(generics.CreateAPIView):
    serializer_class = LogoutAllSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={}, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Logged out from all devices successfully",
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


# ---------------Password  Otp View for User Password Update -------------
class SendPasswordUpdateOTPView(generics.CreateAPIView):
    serializer_class = SendPasswordUpdateOTPSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        otp = serializer.save()

        return Response(
            {
                "message": "OTP sent successfully for password update",
                "expires_at": otp.expires_at,
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


# ---------------Password Confirm View for User Password Update -------------
class UpdatePasswordConfirmView(generics.CreateAPIView):
    serializer_class = VerifyOTPAndUpdatePasswordSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Password updated successfully. Please login again.",
                "relogin_required": True,
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


# ---------------Forget Password  Otp View for User Forget Password Forget -------------
class SendForgetPasswordOTPView(generics.CreateAPIView):
    serializer_class = SendForgetPasswordOTPSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        otp = serializer.save()

        return Response(
            {
                "message": "OTP sent for password reset",
                "expires_at": otp.expires_at,
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


# ---------------Forget Password  Confirm View for User Password Forget -------------
class ForgetPasswordConfirmView(generics.CreateAPIView):
    serializer_class = VerifyOTPAndResetPasswordSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Password reset successful. Please login again.",
                "relogin_required": True,
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


# ---------------Delete User  Otp View for User Delete User -------------
class SendUserDeleteOTPView(generics.CreateAPIView):
    serializer_class = SendUserDeleteOTPSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        otp = serializer.save()

        return Response(
            {
                "message": "OTP sent for account deletion",
                "expires_at": otp.expires_at,
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


# ---------------Delete User  Confirm View for User Delete User -------------
class DeleteUserConfirmView(generics.CreateAPIView):
    serializer_class = VerifyOTPAndDeleteUserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Account deleted successfully",
                "relogin_required": True,
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


@api_view(["GET"])
def home(request):

    books_base_url = reverse("books:books-list", request=request)
    authors_base_url = reverse("author:author-list", request=request)
    category_base_url = reverse("category:category-list", request=request)
    cartitem_base_url = reverse("cartitem:cartitem-list", request=request)
    cart_base_url = reverse("cart:cart-list", request=request)
    users_base_url = reverse("users:user-list", request=request)

    info = {
        "home": reverse("home", request=request),
        "status": reverse("status", request=request),
        "Books": {
            "Book_Status": {
                "total_books": Books.objects.all().count(),
                "total_available_books": Books.objects.filter(
                    availability__iexact="available"
                ).count(),
                "total_maintenance_books": Books.objects.filter(
                    availability__iexact="maintenance"
                ).count(),
                "total_borrowed_books": Books.objects.filter(
                    availability__iexact="borrowed"
                ).count(),
                "total_pending_books": Books.objects.filter(
                    availability__iexact="pending"
                ).count(),
                "total_hindi_books": Books.objects.filter(
                    language__iexact="hindi"
                ).count(),
                "total_urdu_books": Books.objects.filter(
                    language__iexact="urdu"
                ).count(),
                "total_english_books": Books.objects.filter(
                    language__iexact="english"
                ).count(),
                "total_hardcover_books": Books.objects.filter(
                    binding_types__iexact="hardcover"
                ).count(),
                "total_softcover_books": Books.objects.filter(
                    binding_types__iexact="softcover"
                ).count(),
                "total_stitching_books": Books.objects.filter(
                    binding_types__iexact="stitching"
                ).count(),
                "total_spiral_books": Books.objects.filter(
                    binding_types__iexact="spiral"
                ).count(),
                "total_limited_books": Books.objects.filter(
                    edition__iexact="limited"
                ).count(),
                "total_bulk_books": Books.objects.filter(
                    edition__iexact="bulk"
                ).count(),
                "total_special_books": Books.objects.filter(
                    edition__iexact="special"
                ).count(),
            },
            "Books_route": {
                "books_list/create": books_base_url,
                "books_detail/update/delete": reverse(
                    "books:books-detail",
                    kwargs={"pk": "81c45249307b4806b3ae70d3fe9f7138"},
                    request=request,
                ),
            },
            "Book_filters": {
                "Description": "Use '?field=<value>' to filter across multiple fields",
                "By_author": f"{books_base_url}?author=author1",
                "By_category": f"{books_base_url}?category=Technology",
                "By_min-price": f"{books_base_url}?min-price=250",
                "By_max-price": f"{books_base_url}?max-price=250",
                "By_edition": f"{books_base_url}?edition=special",
                "By_publications": f"{books_base_url}?publications=anwar",
                "By_language": f"{books_base_url}?language=hindi",
                "By_isbn": f"{books_base_url}?isbn=978-1-4028-9462-2",
                "By_title": f"{books_base_url}?title=DRF",
                "By_binding_types": f"{books_base_url}?binding_types=hardcover",
            },
            "Book_Search": {
                "Description": "Use '?search=<value>' to look across multiple fields",
                "By_author": f"{books_base_url}?search=author1",
                "By_category": f"{books_base_url}?search=Technology",
                "By_isbn": f"{books_base_url}?search=978-1-4028-9462-2",
                "By_title": f"{books_base_url}?search=DRF",
            },
            "Book_Ordering": {
                "Description": "Use '-fieldname' for descending order (e.g., -price)",
                "By_id": f"{books_base_url}?ordering=id",
                "By_title": f"{books_base_url}?ordering=title",
                "By_author": f"{books_base_url}?ordering=author",
                "By_category": f"{books_base_url}?ordering=category",
                "By_price": f"{books_base_url}?ordering=price",
                "By_publication_date": f"{books_base_url}?ordering=publication_date",
            },
        },
        "Author": {
            "Author_Status": {
                "total_authors": Author.objects.all().count(),
                "total_Verified_authors": Author.objects.filter(
                    is_verified__iexact="True"
                ).count(),
                "total_UnVerified_authors": Author.objects.filter(
                    is_verified__iexact="False"
                ).count(),
            },
            "Author_routes": {
                "author_list/create": authors_base_url,
                "author_detail/update/delete": reverse(
                    "author:author-detail",
                    kwargs={"pk": "e4555587ca2d41d89670ffd27ac17801"},
                    request=request,
                ),
            },
            "Author_filter": {
                "Description": "Use '?field=<value>' to filter across multiple fields",
                "By_id": f"{authors_base_url}?id=e4555587ca2d41d89670ffd27ac17801",
                "By_username": f"{authors_base_url}?username=author1",
                "By_first_name": f"{authors_base_url}?first_name=Author",
                "By_last_name": f"{authors_base_url}?last_name=One",
                "By_email": f"{authors_base_url}?email=author1@gmail.com",
                "By_mobile": f"{authors_base_url}?mobile=9000000011",
                "By_is_Verified": f"{authors_base_url}?is_verified=true",
            },
            "Author_Search": {
                "Description": "Use '?search=<value>' to look across multiple fields",
                "By_id": f"{authors_base_url}?search=e4555587ca2d41d89670ffd27ac17801",
                "By_username": f"{authors_base_url}?search=author1",
                "By_first_name": f"{authors_base_url}?search=Author",
                "By_last_name": f"{authors_base_url}?search=One",
                "By_email": f"{authors_base_url}?search=author1@gmail.com",
                "By_mobile": f"{authors_base_url}?search=9000000011",
                "By_is_Verified": f"{authors_base_url}?search=true",
            },
            "Author_Ordering": {
                "Description": "Use '-fieldname' for descending order (e.g., email)",
                "By_id": f"{authors_base_url}?ordering=id",
                "By_username": f"{authors_base_url}?ordering=username",
                "By_first_name": f"{authors_base_url}?ordering=first_name",
                "By_last_name": f"{authors_base_url}?ordering=last_name",
                "By_email": f"{authors_base_url}?ordering=email",
                "By_mobile": f"{authors_base_url}?ordering=mobile",
                "By_is_Verified": f"{authors_base_url}?ordering=is_verified",
            },
        },
        "Category": {
            "Category_Status": {
                "total_category": Category.objects.all().count(),
                "total_indian_category": Category.objects.filter(
                    origin__iexact="india"
                ).count(),
                "total_foreign_category": Category.objects.filter(
                    origin__iexact="foreign"
                ).count(),
            },
            "Category_routes": {
                "category_list/create": category_base_url,
                "category_detail/update/delete": reverse(
                    "category:category-detail",
                    kwargs={"pk": "81c45249307b4806b3ae70d3fe9f7138"},
                    request=request,
                ),
            },
            "Category_filters": {
                "Description": "Use '?field=<value>' to filter across multiple fields",
                "By_id": f"{category_base_url}?id=81c45249307b4806b3ae70d3fe9f7138",
                "By_category": f"{category_base_url}?category=Technology",
                "By_origin": f"{category_base_url}?origin=India",
            },
            "Category_Search": {
                "Description": "Use '?search=<value>' to look across multiple fields",
                "By_id": f"{category_base_url}?search=81c45249307b4806b3ae70d3fe9f7138",
                "By_category": f"{category_base_url}?search=Technology",
                "By_origin": f"{category_base_url}?search=India",
            },
            "Category_Ordering": {
                "Description": "Use '-fieldname' for descending order (e.g., -origin)",
                "By_id": f"{category_base_url}?ordering=id",
                "By_category": f"{category_base_url}?ordering=category_name",
                "By_origin": f"{category_base_url}?ordering=origin",
            },
        },
        "Cartitem": {
            "Cartitem_routes": {
                "cartitem_list/create": cartitem_base_url,
                "cartitem_detail/update/delete": reverse(
                    "cartitem:cartitem-detail",
                    kwargs={"pk": "item-uuid-ya-id"},
                    request=request,
                ),
            },
            "Cartitem_filter": {
                "Description": "Use '?field=<value>' to filter across multiple fields",
                "id": f"{cartitem_base_url}?id=5c51e1ddbe4b4014976ec8d97a28dc76",
                "By_username": f"{cartitem_base_url}?username=basic3",
                "By_first_name": f"{cartitem_base_url}?first_name=Basic",
                "By_last_name": f"{cartitem_base_url}?last_name=Three",
                "By_Books_title": f"{cartitem_base_url}?book_title=Python",
                "By_quantity": f"{cartitem_base_url}?quantity=2",
                "By_min_price": f"{cartitem_base_url}?min_price=100",
                "By_max_price": f"{cartitem_base_url}?max_price=500",
            },
            "Cartitem_Search": {
                "Description": "Use '?search=<value>' to look across multiple fields",
                "By_id": f"{cartitem_base_url}?search=5c51e1ddbe4b4014976ec8d97a28dc76",
                "By_username": f"{cartitem_base_url}?search=basic3",
                "By_first_name": f"{cartitem_base_url}?search=Basic",
                "By_last_name": f"{cartitem_base_url}?search=Three",
                "By_Books_title": f"{cartitem_base_url}?search=Python",
                "By_quantity": f"{cartitem_base_url}?search=2",
                "By_price": f"{cartitem_base_url}?search=199.00",
            },
            "Cartitem_Ordering": {
                "Description": "Use '-fieldname' for descending order (e.g., quantity)",
                "id": f"{cartitem_base_url}?ordering=id",
                "By_username": f"{cartitem_base_url}?ordering=username",
                "By_first_name": f"{cartitem_base_url}?ordering=first_name",
                "By_last_name": f"{cartitem_base_url}?ordering=last_name",
                "By_Books_title": f"{cartitem_base_url}?ordering=book_title",
                "By_quantity": f"{cartitem_base_url}?ordering=quantity",
                "By_price": f"{cartitem_base_url}?ordering=book_price",
            },
        },
        "Cart_routes": {
            "cart_list": cart_base_url,
            "cart_detail/update/delete": reverse(
                "cart:cart-detail",
                kwargs={"pk": "c5e1f76718374c6c832db6633ba827a4"},
                request=request,
            ),
        },
        "User": {
            "User_routes": {
                "users": users_base_url,
                "users-details": reverse(
                    "users:user-detail",
                    kwargs={"pk": "ca84c553e6014f2093e978ea59359c3c"},
                    request=request,
                ),
            },
            "Auth_Actions": {
                "Registration": {
                    "send_register_otp": reverse("apps:send-otp", request=request),
                    "confirm_register": reverse("apps:register", request=request),
                },
                "Login_Logout": {
                    "send_login_otp": reverse("apps:login-send-otp", request=request),
                    "login_confirm": reverse("apps:login", request=request),
                    "logout": reverse("apps:logout", request=request),
                    "logout_all_devices": reverse("apps:logout-all", request=request),
                },
                "JWT_Tokens": {
                    "refresh": reverse("apps:token-refresh", request=request),
                    "verify": reverse("apps:token-verify", request=request),
                },
            },
            "Account_Security": {
                "Password_Update": {
                    "send_otp": reverse("apps:pwd-update-otp", request=request),
                    "confirm": reverse("apps:pwd-update-confirm", request=request),
                },
                "Forget_Password": {
                    "send_otp": reverse("apps:forget-pwd-otp", request=request),
                    "confirm": reverse("apps:forget-pwd-confirm", request=request),
                },
                "Delete_Account": {
                    "send_otp": reverse("apps:delete-user-otp", request=request),
                    "confirm": reverse("apps:delete-user-confirm", request=request),
                },
            },
            "users_filter": {
                "Description": "Use '?field=<value>' to filter across multiple fields",
                "id": f"{users_base_url}?id=ca84c553e6014f2093e978ea59359c3c",
                "By_username": f"{users_base_url}?username=basic1",
                "By_first_name": f"{users_base_url}?first_name=Basic",
                "By_last_name": f"{users_base_url}?last_name=One",
                "By_email": f"{users_base_url}?email=basic1@gmail.com",
                "By_mobile": f"{users_base_url}?mobile=9000000001",
                "By_is_Verified": f"{users_base_url}?is_verified=true",
            },
            "User_Search": {
                "Description": "Use '?search=<value>' to look across multiple fields",
                "id": f"{users_base_url}?search=ca84c553e6014f2093e978ea59359c3c",
                "By_username": f"{users_base_url}?search=basic1",
                "By_first_name": f"{users_base_url}?search=Basic",
                "By_last_name": f"{users_base_url}?search=One",
                "By_email": f"{users_base_url}?search=basic1@gmail.com",
                "By_mobile": f"{users_base_url}?search=9000000001",
            },
            "User_Ordering": {
                "Description": "Use '-fieldname' for descending order (e.g., email)",
                "id": f"{users_base_url}?ordering=id",
                "By_username": f"{users_base_url}?ordering=username",
                "By_first_name": f"{users_base_url}?ordering=first_name",
                "By_last_name": f"{users_base_url}?ordering=last_name",
                "By_email": f"{users_base_url}?ordering=email",
                "By_mobile": f"{users_base_url}?ordering=mobile",
                "By_is_Verified": f"{users_base_url}?ordering=is_verified",
            },
        },
        "Stats": reverse("status", request=request),
    }
    return Response(
        {
            "msg": "Data fetched successfully",
            "data": info,
            "status": status.HTTP_200_OK,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def stats(request):
    stats = {
        "total_books": Books.objects.count(),
        "total_authors": Author.objects.count(),
        "total_categories": Category.objects.count(),
        "author_by_category": {},
        "books_by_author": {},
        "books_by_binding": {},
        "books_by_availability": {},
        "books_by_edition": {},
        "books_by_language": {},
        "category_by_origin": {},
        "books_by_category": {},
    }

    # books by category
    for category in Category.objects.all():
        stats["books_by_category"][
            category.category_name
        ] = category.category_of_books.count()

    # books by author
    for author in Author.objects.all():
        stats["books_by_author"][author.user.username] = author.books_of_author.count()

    for category in Category.objects.all():
        stats["author_by_category"][category.category_name] = {}

        for author in Author.objects.all():
            count = category.category_of_books.filter(author=author).count()

            if count > 0:
                stats["author_by_category"][category.category_name][
                    author.user.username
                ] = count

    # books by availability
    for choice in Books.AVAILABILITY_CHOICES:
        status_key = choice[0]
        status_label = choice[1]
        counts = Books.objects.filter(availability=status_key).count()
        stats["books_by_availability"][status_label] = counts

    # books by language
    for choice in Books.LANGUAGE_CHOICES:
        status_key = choice[0]
        status_label = choice[1]
        counts = Books.objects.filter(language=status_key).count()
        stats["books_by_language"][status_label] = counts

    # books by binding
    for choice in Books.BINDING_CHOICES:
        status_key = choice[0]
        status_label = choice[1]
        counts = Books.objects.filter(binding_types=status_key).count()
        stats["books_by_binding"][status_label] = counts

    # books by edition
    for choice in Books.EDITION_CHOICES:
        status_key = choice[0]
        status_label = choice[1]
        counts = Books.objects.filter(edition=status_key).count()
        stats["books_by_edition"][status_label] = counts

    # category_by_origin
    for choice in Category.ORIGIN_CHOICES:
        status_key = choice[0]
        status_label = choice[1]
        counts = Category.objects.filter(origin=status_key).count()
        stats["category_by_origin"][status_label] = counts
    return Response(
        {
            "msg": "Data fetched successfully",
            "stats": stats,
            "status": status.HTTP_200_OK,
        },
        status=status.HTTP_200_OK,
    )


def Invalid_Url(request, exception):
    return JsonResponse(
        {
            "msg": "Invalid URL. Please check your endpoint. Try /api or /api/v1/.",
            "path": request.get_full_path(),
            "method": request.method,
            "status": 404,
        },
        status=404,
    )
