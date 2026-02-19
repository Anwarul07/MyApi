import uuid
from django.db import models

# Create your models here.


# ---Category Model ---
class Category(models.Model):
    ORIGIN_CHOICES = [
        ("india", "Indian"),
        ("foreign", "Foreign"),
    ]
    category_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Images (optional)
    cover_image = models.ImageField(upload_to="category/", blank=True, null=True)
    front_image = models.ImageField(upload_to="category/", blank=True, null=True)
    behind_image = models.ImageField(upload_to="category/", blank=True, null=True)
    side_image = models.ImageField(upload_to="category/", blank=True, null=True)
    top_image = models.ImageField(upload_to="category/", blank=True, null=True)
    bottom_image = models.ImageField(upload_to="category/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    origin = models.CharField(max_length=10, choices=ORIGIN_CHOICES, default="india")

    class Meta:
        ordering = ["category_name"]

    def __str__(self):
        return self.category_name
