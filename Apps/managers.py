from django.core.exceptions import ValidationError
from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):

    def create_user(
        self, username, email, mobile, password=None, role=None, **extra_fields
    ):
        """
        Create a normal user (Author or Basic User) only.
        Admin creation from API is blocked.
        """
        from .models import CustomUser

        if not username:
            raise ValueError("The Username must be set")
        if not email:
            raise ValueError("The Email must be set")
        if not mobile:
            raise ValueError("The Mobile number must be set")

        # Valid role check
        role_choices = [choice[0] for choice in CustomUser.ROLE_CHOICES]
        if role not in role_choices:
            raise ValidationError(f"Role must be one of {role_choices}")

        if role == "admin" and not extra_fields.get("is_superuser", False):
            raise ValueError("Admin cannot be created from API or signup.")

        if not email:
            raise ValueError("Email is required")
        if not username:
            raise ValueError("Username is required")

        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            mobile=mobile,
            role=role,
            **extra_fields,
        )

        if password:
            user.set_password(password)

        user.save(using=self._db)
        print(f"User {username} created for  {role} Role")
        return user

    def create_superuser(self, username, email, mobile, password=None, **extra_fields):
        """
        Superuser always has ADMIN role.
        Admin creation ONLY here via command line.
        Max 2 admins allowed.
        """
        from .models import CustomUser

        # Check existing admin count
        admin_count = CustomUser.objects.filter(role=CustomUser.ADMIN).count()
        if admin_count > 1:
            raise ValidationError("Maximum number of Admin users reached (2).")

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", CustomUser.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("role") != CustomUser.ADMIN:
            raise ValueError("Superuser role must always be ADMIN.")

        if not email:
            raise ValueError("Email is required")
        if not username:
            raise ValueError("Username is required")

        email = self.normalize_email(email)

        print(f"User {username} created for  Admin Role")
        return self.create_user(
            username=username,
            email=email,
            mobile=mobile,
            password=password,
            **extra_fields,
        )
