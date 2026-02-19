from UserApp.models import CustomUser
from AuthorApp.models import Author
from BookApp.models import Books
from CategoryApp.models import Category
from CategoryApp.serializers import CategorySerializer
from rest_framework import serializers


# ---------------- Author Create Serializer for Author details----------------
class AuthorSerializer(serializers.ModelSerializer):

    # User related fields
    id = serializers.UUIDField(format="hex", read_only=True)
    user_id = serializers.CharField(source="user.id", read_only=True)
    role = serializers.CharField(source="user.role", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    mobile = serializers.CharField(source="user.mobile", read_only=True)

    cover_image = serializers.ImageField(source="user.cover_image", read_only=True)
    front_image = serializers.ImageField(source="user.front_image", read_only=True)
    behind_image = serializers.ImageField(source="user.behind_image", read_only=True)
    side_image = serializers.ImageField(source="user.side_image", read_only=True)
    top_image = serializers.ImageField(source="user.top_image", read_only=True)
    bottom_image = serializers.ImageField(source="user.bottom_image", read_only=True)

    # Books reverse relation -> from Books model: author = FK(CustomUser)
    # books_of_author = BooksReadSerializer(
    #     source="user.books", many=True, read_only=True
    # )

    # Aggregates
    totalbooks = serializers.SerializerMethodField()
    totalcategory = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role="author")
    )

    # category_of_books = serializers.SerializerMethodField() --->
    # books_of_author = serializers.SerializerMethodField() --->

    class Meta:
        model = Author
        fields = "__all__"

        read_only_fields = [
            "username",
            "email",
            "mobile",
            "totalbooks",
            "totalcategory",
            # "category_of_books", --->
            # "books_of_author", --->
        ]

    def validate_user(self, value):
        request = self.context.get("request")
        user = request.user

        if not user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")
        if value.role != "author":
            raise serializers.ValidationError(
                "Only  Author users can be assigned as book author."
            )
        return value

    def validate_is_verified(self, value):
        request = self.context.get("request")
        if request is None:
            return value

        user = request.user
        instance = getattr(self, "instance", None)

        # ---------------- CREATE ----------------
        if instance is None:
            if user.role == "author":
                if "is_verified" in request.data:
                    raise serializers.ValidationError(
                        "Authors cannot update verification status. Admin approval required."
                    )
                return False
            return value

        # ---------------- UPDATE ----------------
        old_value = instance.is_verified
        if value != old_value and user.role != "admin":
            raise serializers.ValidationError(
                "Authors cannot update verification status. Admin approval required."
            )

        return value

    def get_fields(self):
        fields = super().get_fields()

        request = self.context.get("request")
        if not request:
            return fields  # serializer context me request nahi hai

        user = request.user

        if not user.is_superuser:
            fields.pop("user", None)

        return fields

    # ------------------------ AGGREGATION ------------------------

    def get_totalbooks(self, obj):
        return obj.books_of_author.count()

    def get_totalcategory(self, obj):
        return obj.books_of_author.values_list("category", flat=True).distinct().count()

    # def get_books_of_author(self, obj):
    #     from BookApp.serializers import BooksReadSerializer
    #     books = Books.objects.filter(author=obj)
    #     return BooksReadSerializer(books, many=True, context=self.context).data

    # def get_category_of_books(self, obj):
    #     categories = Category.objects.filter(category_of_books__author=obj).distinct()
    #     return CategoryReadSerializer(categories, many=True).data
