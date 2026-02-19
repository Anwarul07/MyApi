from UserApp.models import CustomUser
from rest_framework import serializers
from CartApp.models import Cart

# ---------------- Cart Create Serializer for Cart details----------------
class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(format="hex", read_only=True)

    # user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    mobile = serializers.CharField(source="user.mobile", read_only=True, default=None)

    items = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role="basic_user")
    )

    class Meta:
        model = Cart
        fields = "__all__"

    def get_items(self, obj):
        from Cartitem.serializers import CartItemSerializer

        cart_items = obj.user.carts.all()
        return CartItemSerializer(cart_items, many=True).data

    def get_total_amount(self, obj):
        cart_items = obj.user.carts.all()
        return sum(item.total for item in cart_items)

    def validate_user(self, value):
        if value.role != "basic_user":
            raise serializers.ValidationError(
                "Only buyer users can be assigned as cart."
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
