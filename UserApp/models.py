import uuid
from django.db import models
from Apps.managers import CustomUserManager
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


# Create your models here.


# ---Custom user Model ---
class CustomUser(AbstractUser):
    # --- Roles ---
    ADMIN = "admin"
    AUTHOR = "author"
    BASIC_USER = "basic_user"
    ROLE_CHOICES = (
        (ADMIN, "Admin"),
        (AUTHOR, "Author"),
        (BASIC_USER, "Basic User"),
    )

    # --- User Info ---
    mobile = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=BASIC_USER)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # --- Optional Images ---
    cover_image = models.ImageField(upload_to="users/", blank=True, null=True)
    front_image = models.ImageField(upload_to="users/", blank=True, null=True)
    behind_image = models.ImageField(upload_to="users/", blank=True, null=True)
    side_image = models.ImageField(upload_to="users/", blank=True, null=True)
    top_image = models.ImageField(upload_to="users/", blank=True, null=True)
    bottom_image = models.ImageField(upload_to="users/", blank=True, null=True)

    # --- Custom Manager ---
    objects = CustomUserManager()

    # --- Authentication --
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["mobile", "username"]

    # --- String Representation ---
    def __str__(self):
        return self.username
