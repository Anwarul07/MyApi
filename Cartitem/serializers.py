from UserApp.models import CustomUser
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

from Cartitem.models import CartItem


# ---------------- CartItem Create Serializer for CartItem details----------------


class CartItemSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(format="hex", read_only=True)

    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    book_title = serializers.CharField(source="books.title", read_only=True)

    book_price = serializers.DecimalField(
        source="books.price", max_digits=10, decimal_places=2, read_only=True
    )
    book_discount = serializers.DecimalField(
        source="books.discount", max_digits=5, decimal_places=2, read_only=True
    )

    sale_price = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role="basic_user")
    )

    class Meta:
        model = CartItem
        fields = "__all__"
        read_only_fields = ("added_at", "updated_at")

    # ---------- Sale Price (discount applied) ----------
    def get_sale_price(self, obj):
        return obj.sale_price  # model property calculation

    # ---------- Total Price (quantity × sale_price) ----------
    def get_total(self, obj):
        return obj.total  # model property calculation

    def validate_user(self, value):
        if value.role != "basic_user":
            raise serializers.ValidationError(
                "Only buyer users can be assigned as cartitem author."
            )
        return value

    # ---------- Restrict update (user/books cannot change) ----------
    def update(self, instance, validated_data):
        request = self.context.get("request")

        # Buyers cannot change user or books
        if request.user.role == "basic_user":
            validated_data.pop("user", None)

        # Authors cannot change user or books (not allowed anyway)
        if request.user.role == "author":
            validated_data.pop("user", None)

        # Admin can change user, but cannot change books
        if request.user.role in ["admin"] or request.user.is_superuser:
            return super().update(instance, validated_data)

        return super().update(instance, validated_data)

    def get_fields(self):
        fields = super().get_fields()

        request = self.context.get("request")
        if not request:
            return fields  # serializer context me request nahi hai

        user = request.user

        if not user.is_superuser:
            fields.pop("user", None)

        return fields
