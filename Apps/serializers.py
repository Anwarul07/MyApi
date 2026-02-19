from Apps.otp import *
from UserApp.models import CustomUser
from django.db.models import Q
from django.db import transaction
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)

User = get_user_model()


# ---------------- OTP Serializer for OTP details----------------


class SendOTPSerializer(serializers.Serializer):
    otp_via = serializers.ChoiceField(choices=[OTP.EMAIL, OTP.SMS], default=OTP.SMS)
    email = serializers.EmailField(required=False)
    mobile = serializers.CharField(max_length=10, required=False)

    def validate(self, data):
        if data["otp_via"] == OTP.EMAIL and not data.get("email"):
            raise serializers.ValidationError("Email required")

        if data["otp_via"] == OTP.SMS and not data.get("mobile"):
            raise serializers.ValidationError("Mobile required")

        one_min_ago = timezone.now() - timedelta(minutes=1)

        if data.get("email"):
            if OTP.objects.filter(
                email=data["email"],
                purpose=OTP.REGISTRATION,
                created_at__gte=one_min_ago,
            ).exists():
                raise serializers.ValidationError(
                    "Please wait 1 minute before requesting another OTP"
                )

        if data.get("mobile"):
            if OTP.objects.filter(
                mobile=data["mobile"],
                purpose=OTP.REGISTRATION,
                created_at__gte=one_min_ago,
            ).exists():
                raise serializers.ValidationError(
                    "Please wait 1 minute before requesting another OTP"
                )

        # Already registered checks
        if data.get("email") and User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError("Email already registered")

        if data.get("mobile") and User.objects.filter(mobile=data["mobile"]).exists():
            raise serializers.ValidationError("Mobile already registered")

        return data

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data.get("email")
        mobile = validated_data.get("mobile")
        otp_via = validated_data["otp_via"]

        #  delete old unused OTPs
        if otp_via == OTP.EMAIL:
            OTP.objects.filter(
                email=email, is_used=False, purpose=OTP.REGISTRATION
            ).delete()
        else:
            OTP.objects.filter(
                mobile=mobile, is_used=False, purpose=OTP.REGISTRATION
            ).delete()

        otp_code = generate_otp()  # 6-digit
        hashed_otp = make_password(otp_code)
        expiry_time = get_expiry_time()  # now + 5 minutes

        otp = OTP.objects.create(
            user=None,
            email=email,
            mobile=mobile,
            otp_via=otp_via,
            otp=hashed_otp,
            expires_at=get_expiry_time(),
            purpose=OTP.REGISTRATION,
            attempts=0,
        )

        #  send OTP
        if otp_via == OTP.EMAIL:
            send_email_otp(email, otp_code)
        else:
            send_sms_otp(mobile, otp_code)

        return otp


# ---------------- VerifyOtp and Register User Serializer User Registration ----------------


class VerifyOTPAndRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    mobile = serializers.CharField(max_length=10, required=True)  # REQUIRED FOR USER
    otp = serializers.CharField(write_only=True)

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[CustomUser.AUTHOR, CustomUser.BASIC_USER])

    def validate_mobile(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Invalid mobile number format")
        if CustomUser.objects.filter(mobile=value).exists():
            raise serializers.ValidationError("Mobile already registered")
        return value

    def validate(self, data):
        filters = Q(
            purpose=OTP.REGISTRATION,
            is_used=False,
            user__isnull=True,
        )

        if data.get("email"):
            filters &= Q(email=data["email"])

        otp_obj = OTP.objects.filter(filters).order_by("-created_at").first()

        if not otp_obj:
            raise serializers.ValidationError("Invalid OTP or credentials")

        # medium-based strict match
        if otp_obj.otp_via == OTP.EMAIL:
            if otp_obj.email != data.get("email"):
                raise serializers.ValidationError(
                    "OTP was sent to email. Please use the same email."
                )

        if otp_obj.otp_via == OTP.SMS:
            if otp_obj.mobile != data.get("mobile"):
                raise serializers.ValidationError(
                    "OTP was sent to mobile. Please use the same mobile."
                )

        if otp_obj.is_expired():
            raise serializers.ValidationError("OTP expired")

        if not check_password(data["otp"], otp_obj.otp):
            otp_obj.attempts += 1
            otp_obj.save(update_fields=["attempts"])
            raise serializers.ValidationError("Invalid OTP")

        data["otp_obj"] = otp_obj
        return data

    def create(self, validated_data):
        otp_obj = validated_data.pop("otp_obj")
        validated_data.pop("otp")
        password = validated_data.pop("password")
        role = validated_data.pop("role")

        # OTP consume
        otp_obj.is_used = True
        otp_obj.save(update_fields=["is_used"])
        user = CustomUser.objects.create_user(
            password=password,
            role=role,
            **validated_data,
        )

        # Role-based flags
        if role == CustomUser.AUTHOR:
            user.is_staff = True

        user.save()
        return user


# ---------------- SendOtp Login  Serializer User Login ----------------


class SendLoginOTPSerializer(serializers.Serializer):
    otp_via = serializers.ChoiceField(choices=[OTP.EMAIL, OTP.SMS])
    email = serializers.EmailField(required=False)
    mobile = serializers.CharField(required=False)

    def validate(self, data):
        if data["otp_via"] == OTP.EMAIL and not data.get("email"):
            raise serializers.ValidationError("Email required.")

        if data["otp_via"] == OTP.SMS and not data.get("mobile"):
            raise serializers.ValidationError("Mobile required.")

        # User must exist
        if data.get("email"):
            user = CustomUser.objects.filter(email=data["email"]).first()
        else:
            user = CustomUser.objects.filter(mobile=data["mobile"]).first()

        if not user:
            raise serializers.ValidationError("User not registered.")

        data["user"] = user
        return data

    def create(self, validated_data):
        user = validated_data["user"]
        otp_via = validated_data["otp_via"]

        # Delete old unused LOGIN OTPs for this user
        OTP.objects.filter(
            user=user,
            purpose=OTP.LOGIN,
            is_used=False,
        ).delete()

        otp_code = generate_otp()
        hashed_otp = make_password(otp_code)

        otp = OTP.objects.create(
            user=user,
            email=user.email,
            mobile=user.mobile,
            otp_via=otp_via,
            otp=hashed_otp,
            expires_at=get_expiry_time(),
            purpose=OTP.LOGIN,
            attempts=0,
        )

        # SEND OTP
        if otp_via == OTP.EMAIL:
            send_email_otp(user.email, otp_code)
        else:
            send_sms_otp(user.mobile, otp_code)

        return otp


# ---------------- Login  Serializer User Login ----------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    mobile = serializers.CharField(required=False)
    password = serializers.CharField(required=False, write_only=True)
    otp = serializers.CharField(required=False, write_only=True)

    def validate(self, data):
        email = data.get("email")
        mobile = data.get("mobile")
        password = data.get("password")
        otp = data.get("otp")

        # ---------- BASIC VALIDATIONS ----------
        if not email and not mobile:
            raise serializers.ValidationError("Email or mobile is required.")

        if email and mobile:
            raise serializers.ValidationError(
                "Provide either email or mobile, not both."
            )

        if not password and not otp:
            raise serializers.ValidationError("Password or OTP is required.")

        if password and otp:
            raise serializers.ValidationError(
                "Provide either password or OTP, not both."
            )

        # ---------- FIND USER ----------
        user = (
            CustomUser.objects.filter(email=email).first()
            if email
            else CustomUser.objects.filter(mobile=mobile).first()
        )

        if not user:
            raise serializers.ValidationError("User not found.")

        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")

        # ---------- PASSWORD LOGIN ----------
        if password:
            if not user.has_usable_password():
                raise serializers.ValidationError(
                    "Password login is not enabled for this account."
                )

            user = authenticate(email=user.email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials.")

        # ---------- OTP LOGIN ----------
        if otp:
            otp_obj = (
                OTP.objects.filter(
                    user=user,
                    purpose=OTP.LOGIN,
                    is_used=False,
                )
                .order_by("-created_at")
                .first()
            )

            if not otp_obj:
                raise serializers.ValidationError("Invalid OTP.")

            if otp_obj.is_expired():
                raise serializers.ValidationError("OTP expired.")

            if otp_obj.attempts >= 5:
                raise serializers.ValidationError(
                    "OTP blocked. Please request a new OTP."
                )

            if not check_password(otp, otp_obj.otp):
                otp_obj.attempts += 1
                otp_obj.save(update_fields=["attempts"])
                raise serializers.ValidationError("Invalid OTP.")

            #  consume OTP
            otp_obj.is_used = True
            otp_obj.save(update_fields=["is_used"])

        data["user"] = user
        return data

    def create(self, validated_data):
        user = validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_id": user.id,
            "email": user.email,
            "mobile": user.mobile,
            "role": user.role,
        }


# ---------------- Logout  Serializer User Logout ----------------
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.validated_data["refresh"])
            token.blacklist()
        except TokenError:
            raise serializers.ValidationError("Invalid or expired refresh token")


# ---------------- Logout from all device Serializer User Logout ----------------
class LogoutAllSerializer(serializers.Serializer):

    def save(self, **kwargs):
        user = self.context["request"].user
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        tokens = OutstandingToken.objects.filter(user=user).exclude(
            blacklistedtoken__isnull=False
        )

        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)
        return {"detail": "Logged out from all devices"}


# ----------------PasswordUpdate otp Based   Serializer Passwoord Update ----------------
class SendPasswordUpdateOTPSerializer(serializers.Serializer):
    otp_via = serializers.ChoiceField(choices=[OTP.EMAIL, OTP.SMS], default=OTP.EMAIL)

    def validate(self, data):
        request = self.context.get("request")
        user = request.user

        if not request or not user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        #  Admin / staff without OTP
        if user.is_superuser:
            raise serializers.ValidationError(
                "Admin password update does not require OTP."
            )

        # medium availability check
        if data["otp_via"] == OTP.EMAIL and not user.email:
            raise serializers.ValidationError("Email not available for this account.")

        if data["otp_via"] == OTP.SMS and not user.mobile:
            raise serializers.ValidationError("Mobile not available for this account.")

        #  RATE LIMIT (1 OTP / minute)
        one_min_ago = timezone.now() - timedelta(minutes=1)
        if OTP.objects.filter(
            user=user,
            purpose=OTP.PASSWORD_UPDATE,
            created_at__gte=one_min_ago,
        ).exists():
            raise serializers.ValidationError(
                "Please wait 1 minute before requesting another OTP."
            )

        return data

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        # Old unsued  OTP delete
        OTP.objects.filter(
            user=user,
            purpose=OTP.PASSWORD_UPDATE,
            is_used=False,
        ).delete()

        otp_code = generate_otp()

        otp = OTP.objects.create(
            user=user,
            email=user.email,
            mobile=user.mobile,
            otp_via=validated_data["otp_via"],
            otp=make_password(otp_code),
            expires_at=get_expiry_time(),
            purpose=OTP.PASSWORD_UPDATE,
            attempts=0,
        )

        #  OTP send via channel
        if validated_data["otp_via"] == OTP.EMAIL:
            send_email_otp(user.email, otp_code)
        else:
            send_sms_otp(user.mobile, otp_code)

        return otp


# ---------------- Update Password   Serializer Password Update  ----------------
class VerifyOTPAndUpdatePasswordSerializer(serializers.Serializer):
    otp = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    refresh = serializers.CharField(write_only=True, required=False)

    def validate(self, data):
        request = self.context.get("request")
        user = request.user

        if not request or not user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        # Admin bypass blocked
        if user.is_superuser:
            raise serializers.ValidationError(
                "Admin must use admin password update API."
            )

        #  Strong password validation
        validate_password(data["new_password"], user=user)

        otp_obj = (
            OTP.objects.filter(
                user=user,
                purpose=OTP.PASSWORD_UPDATE,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )

        if not otp_obj:
            raise serializers.ValidationError("OTP not found.")

        if otp_obj.is_expired():
            otp_obj.is_used = True
            otp_obj.save(update_fields=["is_used"])
            raise serializers.ValidationError("OTP expired.")

        if otp_obj.attempts >= 5:
            raise serializers.ValidationError("OTP blocked. Please request a new OTP.")

        if not check_password(data["otp"], otp_obj.otp):
            otp_obj.attempts += 1
            otp_obj.save(update_fields=["attempts"])
            raise serializers.ValidationError("Invalid OTP.")

        data["otp_obj"] = otp_obj
        return data

    def save(self, **kwargs):
        request = self.context["request"]
        user = request.user
        otp_obj = self.validated_data["otp_obj"]

        #  Password update
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])

        #  OTP consume
        otp_obj.is_used = True
        otp_obj.save(update_fields=["is_used"])

        #  Refresh token blacklist (force re-login)
        refresh_token = self.validated_data.get("refresh")
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except Exception:
                pass

        return user


# ---------------- Password update by Admin   Serializer Password Update By Admin  ----------------
class AdminPasswordUpdateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        request = self.context["request"]
        if not (request.user.is_staff or request.user.is_superuser):
            raise serializers.ValidationError("Permission denied")
        return data

    def save(self):
        user = User.objects.get(id=self.validated_data["user_id"])
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user


# ---------------- Forget Password OTP Serializer Password Update ----------------
class SendForgetPasswordOTPSerializer(serializers.Serializer):
    otp_via = serializers.ChoiceField(choices=[OTP.EMAIL, OTP.SMS])
    email = serializers.EmailField(required=False)
    mobile = serializers.CharField(required=False)

    def validate(self, data):
        if not data.get("email") and not data.get("mobile"):
            raise serializers.ValidationError("Email or mobile is required.")

        if data.get("email") and data.get("mobile"):
            raise serializers.ValidationError(
                "Provide either email or mobile, not both."
            )

        if data["otp_via"] == OTP.EMAIL and not data.get("email"):
            raise serializers.ValidationError("Email required.")

        if data["otp_via"] == OTP.SMS and not data.get("mobile"):
            raise serializers.ValidationError("Mobile required.")

        user = (
            CustomUser.objects.filter(email=data.get("email")).first()
            if data.get("email")
            else CustomUser.objects.filter(mobile=data.get("mobile")).first()
        )

        if not user:
            raise serializers.ValidationError("User not found.")

        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")

        data["user"] = user
        return data

    def create(self, validated_data):
        user = validated_data["user"]
        otp_via = validated_data["otp_via"]

        OTP.objects.filter(
            user=user,
            purpose=OTP.PASSWORD_RESET,
            is_used=False,
        ).delete()

        otp_code = generate_otp()

        otp = OTP.objects.create(
            user=user,
            email=user.email,
            mobile=user.mobile,
            otp_via=otp_via,
            otp=make_password(otp_code),
            expires_at=get_expiry_time(),
            purpose=OTP.PASSWORD_RESET,
            attempts=0,
        )

        if otp_via == OTP.EMAIL:
            send_email_otp(user.email, otp_code)
        else:
            send_sms_otp(user.mobile, otp_code)

        return otp

# ---------------- Forget Password Confirm Serializer Password Forget----------------
class VerifyOTPAndResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    mobile = serializers.CharField(required=False)
    otp = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if not data.get("email") and not data.get("mobile"):
            raise serializers.ValidationError("Email or mobile is required.")

        user = (
            CustomUser.objects.filter(email=data.get("email")).first()
            if data.get("email")
            else CustomUser.objects.filter(mobile=data.get("mobile")).first()
        )

        if not user:
            raise serializers.ValidationError("User not found.")

        validate_password(data["new_password"], user=user)

        otp_obj = (
            OTP.objects.filter(
                user=user,
                purpose=OTP.PASSWORD_RESET,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )

        if not otp_obj:
            raise serializers.ValidationError("OTP not found.")

        if otp_obj.is_expired():
            otp_obj.is_used = True
            otp_obj.save(update_fields=["is_used"])
            raise serializers.ValidationError("OTP expired.")

        if otp_obj.attempts >= 5:
            raise serializers.ValidationError("OTP blocked.")

        if not check_password(data["otp"], otp_obj.otp):
            otp_obj.attempts += 1
            otp_obj.save(update_fields=["attempts"])
            raise serializers.ValidationError("Invalid OTP.")

        data["user"] = user
        data["otp_obj"] = otp_obj
        return data

    def save(self):
        user = self.validated_data["user"]
        otp_obj = self.validated_data["otp_obj"]

        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])

        otp_obj.is_used = True
        otp_obj.save(update_fields=["is_used"])

        #  logout all devices
        tokens = OutstandingToken.objects.filter(user=user).exclude(
            blacklistedtoken__isnull=False
        )
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)

        return user


# ---------------- User delete  OTP Serializer delete user ----------------
class SendUserDeleteOTPSerializer(serializers.Serializer):
    otp_via = serializers.ChoiceField(choices=[OTP.EMAIL, OTP.SMS], default=OTP.EMAIL)

    def validate(self, data):
        request = self.context.get("request")
        user = request.user

        if not request or not user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        # Admin / staff self-delete via OTP blocked
        if user.is_superuser:
            raise serializers.ValidationError(
                "Admin account deletion requires admin intervention."
            )

        if data["otp_via"] == OTP.EMAIL and not user.email:
            raise serializers.ValidationError("Email not available.")

        if data["otp_via"] == OTP.SMS and not user.mobile:
            raise serializers.ValidationError("Mobile not available.")

        return data

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        OTP.objects.filter(
            user=user,
            purpose=OTP.USER_DELETE,
            is_used=False,
        ).delete()

        otp_code = generate_otp()

        otp = OTP.objects.create(
            user=user,
            email=user.email,
            mobile=user.mobile,
            otp_via=validated_data["otp_via"],
            otp=make_password(otp_code),
            expires_at=get_expiry_time(),
            purpose=OTP.USER_DELETE,
            attempts=0,
        )

        if validated_data["otp_via"] == OTP.EMAIL:
            send_email_otp(user.email, otp_code)
        else:
            send_sms_otp(user.mobile, otp_code)

        return otp

# ---------------- User delete confirm OTP Serializer user delete confirm ----------------
class VerifyOTPAndDeleteUserSerializer(serializers.Serializer):
    otp = serializers.CharField(write_only=True)

    def validate(self, data):
        request = self.context.get("request")
        user = request.user

        if not request or not user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        otp_obj = (
            OTP.objects.filter(
                user=user,
                purpose=OTP.USER_DELETE,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )

        if not otp_obj:
            raise serializers.ValidationError("OTP not found.")

        if otp_obj.is_expired():
            otp_obj.is_used = True
            otp_obj.save(update_fields=["is_used"])
            raise serializers.ValidationError("OTP expired.")

        if otp_obj.attempts >= 5:
            raise serializers.ValidationError("OTP blocked. Please request a new OTP.")

        if not check_password(data["otp"], otp_obj.otp):
            otp_obj.attempts += 1
            otp_obj.save(update_fields=["attempts"])
            raise serializers.ValidationError("Invalid OTP.")

        data["otp_obj"] = otp_obj
        return data

    def save(self):
        request = self.context["request"]
        user = request.user
        otp_obj = self.validated_data["otp_obj"]

        #  consume OTP
        otp_obj.is_used = True
        otp_obj.save(update_fields=["is_used"])

        #  logout all devices
        tokens = OutstandingToken.objects.filter(user=user).exclude(
            blacklistedtoken__isnull=False
        )
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)

        #  SOFT DELETE (recommended)
        # user.is_active = False
        # user.save(update_fields=["is_active"])


        user.delete()  # HARD DELETE
        return {"detail": "User account deleted"}

