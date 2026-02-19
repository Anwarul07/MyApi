from Apps.otp import *
from UserApp.models import CustomUser
from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


# ---------------- User Serializer for User details----------------
class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(format="hex", read_only=True)

    role = serializers.ChoiceField(
        choices=[
            (CustomUser.AUTHOR, "Author"),
            (CustomUser.BASIC_USER, "Buyer"),
        ],
        required=True,
    )

    class Meta:
        model = CustomUser
        exclude = ("groups", "user_permissions", "is_active")
        extra_kwargs = {
            "password": {"write_only": True, "required": True},
            "date_joined": {"read_only": True},
            "last_login": {"read_only": True},
            "is_staff": {"read_only": True},
            "is_active": {"read_only": True},
            "is_superuser": {"read_only": True},
        }

    def validate_role(self, value):
        request = self.context.get("request")

        # Always allow serializer to work without request
        if not request:
            return value

        # REGISTER
        if request.method == "POST":
            if value == CustomUser.ADMIN:
                raise serializers.ValidationError("Admin users cannot be registered.")
            return value

        # UPDATE
        if request.method in ["PUT", "PATCH"]:
            user = request.user
            instance = self.instance

            if not user.is_authenticated:
                raise serializers.ValidationError("Authentication required.")

            if instance and value != instance.role and not user.is_superuser:
                raise serializers.ValidationError("Role change is not allowed.")

        return value

    def create(self, validated_data):
        request = self.context.get("request")

        if (
            not request
            or not request.user.is_authenticated
            or not request.user.is_superuser
        ):
            raise serializers.ValidationError(
                "User creation is only allowed via OTP-based registration."
            )

        password = validated_data.pop("password")

        user = CustomUser(**validated_data)
        user.set_password(password)  # hash password

        # Role-based flags
        if user.role == CustomUser.AUTHOR:
            user.is_staff = True

        user.save()
        return user

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = self.context.get("request").user

        password = validated_data.pop("password", None)
        if password:
            if not user or not user.is_superuser:
                raise serializers.ValidationError(
                    "Password can only be changed by admin or via OTP-based flow."
                )
            instance.set_password(password)

        role = validated_data.pop("role", None)

        if role and request and request.user.is_superuser:
            instance.role = role
            instance.is_staff = role == CustomUser.AUTHOR

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def get_fields(self):
        fields = super().get_fields()

        request = self.context.get("request")
        if not request:
            return fields  # serializer context me request nahi hai

        user = request.user

        if not user.is_superuser:
            fields.pop("password", None)
            fields["role"].read_only = True

        return fields
