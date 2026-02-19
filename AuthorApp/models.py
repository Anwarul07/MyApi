import uuid
from django.db import models
from django.conf import settings


# Create your models here.


# ---Author user Model ---
class Author(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="author_profile",
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    biography = models.TextField(max_length=200)
    is_verified = models.BooleanField(default=False)
    date_of_birth = models.DateField()
    short_description = models.TextField()

    def __str__(self):
        return self.user.username
