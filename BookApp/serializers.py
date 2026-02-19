from Apps.otp import *
from decimal import Decimal
from UserApp.models import CustomUser
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()

from BookApp.models import Books
from CategoryApp.serializers import CategorySerializer


# ---------------- Book Create Serializer for Book details----------------
class BooksSerializer(serializers.ModelSerializer):

    id = serializers.UUIDField(format="hex", read_only=True)
    # author_details = AuthorSerializer(read_only=True, source="author")

    # author_details = serializers.SerializerMethodField() --->
    # category_details = CategoryReadSerializer(read_only=True, source="category") --?

    author_name = serializers.SerializerMethodField()
    category_name = serializers.StringRelatedField(source="category")
    sale_price = serializers.SerializerMethodField()

    # Author assignment restricted to users with role "author"
    # author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())

    class Meta:
        model = Books
        fields = "__all__"
        read_only_fields = [
            "author_name",
            "category_name",
            "sale_price",
            "created_at",
            "updated_at",
            # "author_details",
            # "category_details",
        ]

    def get_author_details(self, obj):
        from AuthorApp.serializers import AuthorSerializer

        return AuthorSerializer(obj.author, context=self.context).data

    def get_author_name(self, obj):
        return f"{obj.author.user.username} "
        # return f"{obj.author.user.first_name} {obj.author.user.last_name}"

    def get_sale_price(self, obj):
        discount_percentage = Decimal(obj.discount or 0) / Decimal(100)
        total = obj.price * (Decimal(1) - discount_percentage)
        return round(total, 2)

    def validate_author(self, value):
        request = self.context.get("request")
        user = request.user

        if value.user.role != CustomUser.AUTHOR:
            raise serializers.ValidationError(
                "The associated user must have the role 'author'."
            )

        # if user.role == "author" and value != user.author_profile:
        #     raise serializers.ValidationError(
        #         "Authors cannot change or assign the author field. Only admin can do this."
        #     )
        return value

    def validate_availability(self, value):
        request = self.context.get("request")
        if not request:
            return value
        user = request.user

        if not hasattr(user, "author_profile"):
            return value

        instance = getattr(self, "instance", None)
        if instance is None:
            if "availability" not in request.data:
                raise serializers.ValidationError(
                    "Authors cannot modify availability. Admin approval required."
                )
            return "pending"

        old_value = instance.availability
        if value != old_value:
            raise serializers.ValidationError(
                "Authors cannot modify availability. Admin approval required."
            )

        return value

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user

        # Author but not verified → block
        if user.role == "author" and not user.author_profile.is_verified:
            raise serializers.ValidationError(
                "Only verified authors can create or update books."
            )

        return attrs

    def get_fields(self):
        fields = super().get_fields()

        request = self.context.get("request")
        if not request:
            return fields

        user = request.user

        if not user.is_superuser:
            if "user" in fields:
                fields.pop("user", None)

        return fields
