import uuid
from django.db import models
from UserApp.models import CustomUser
from django.utils import timezone
from .managers import CustomUserManager


# Create your models here.

# ---OTP Model ---


class OTP(models.Model):

    REGISTRATION = "registration"
    LOGIN = "login"
    PASSWORD_RESET = "password_reset"
    PASSWORD_UPDATE = "password_update"
    USER_DELETE = "user_delete"

    PURPOSE_CHOICES = (
        (REGISTRATION, "Registration"),
        (LOGIN, "Login"),
        (PASSWORD_RESET, "Password Reset"),
        (PASSWORD_UPDATE, "Password Update"),
        (USER_DELETE, "User Delete"),
    )

    EMAIL = "email"
    SMS = "sms"

    OTP_VIA = (
        (EMAIL, "Email"),
        (SMS, "SMS/Text Message"),
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="otps",
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=10, blank=True, null=True)

    otp_via = models.CharField(max_length=10, choices=OTP_VIA, default=EMAIL)
    otp = models.CharField(max_length=128)

    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    is_used = models.BooleanField(default=False)

    attempts = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_valid(self):
        return not self.is_used and not self.is_expired() and self.attempts < 5

    def __str__(self):
        return f"OTP({self.user or self.email or self.mobile})"


