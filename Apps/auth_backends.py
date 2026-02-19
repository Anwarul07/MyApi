from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailOrMobileBackend(ModelBackend):
    """
    Authenticate using email OR mobile + password
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        identifier = username.strip()
        mobile = identifier.replace(" ", "").replace("-", "")

        try:
            user = User.objects.get(
                Q(email__iexact=identifier)
                | Q(mobile=mobile if mobile.isdigit() else None)
            )
        except User.DoesNotExist:
            return None

        if user.check_password(password) and user.is_active:
            return user

        return None
