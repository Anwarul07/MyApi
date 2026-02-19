import uuid
from decimal import Decimal
from django.db import models
from AuthorApp.models import Author
from CategoryApp.models import Category
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
# ---Book Model ---


class Books(models.Model):

    # ------------ Choices ------------
    AVAILABILITY_CHOICES = [
        ("available", "Available"),
        ("borrowed", "Borrowed"),
        ("maintenance", "Under Maintenance"),
        ("pending", "Pending for Approval"),
    ]

    LANGUAGE_CHOICES = [
        ("hindi", "Hindi"),
        ("urdu", "Urdu"),
        ("english", "English"),
    ]

    BINDING_CHOICES = [
        ("hardcover", "Hardcover"),
        ("softcover", "Softcover / Papercover"),
        ("stitching", "Stitching"),
        ("spiral", "Spiral"),
    ]

    EDITION_CHOICES = [
        ("limited", "Limited"),
        ("bulk", "Bulk"),
        ("special", "Special"),
    ]

    # ------------ Main Fields ------------
    title = models.CharField(max_length=50, unique=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    author = models.ForeignKey(
        "AuthorApp.Author",
        on_delete=models.CASCADE,
        related_name="books_of_author",
    )

    category = models.ForeignKey(
        "CategoryApp.Category",
        on_delete=models.PROTECT,
        related_name="category_of_books",
    )

    # ------------ Images ------------
    cover_image = models.ImageField(upload_to="books/", blank=True, null=True)
    front_image = models.ImageField(upload_to="books/", blank=True, null=True)
    behind_image = models.ImageField(upload_to="books/", blank=True, null=True)
    side_image = models.ImageField(upload_to="books/", blank=True, null=True)
    top_image = models.ImageField(upload_to="books/", blank=True, null=True)
    bottom_image = models.ImageField(upload_to="books/", blank=True, null=True)

    # ------------ Book Details ------------
    total_pages = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    isbn = models.CharField(max_length=17, unique=True, null=True, blank=True)

    ratings = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        null=True,
        blank=True,
    )

    price = models.DecimalField(
        max_digits=7, decimal_places=2, validators=[MinValueValidator(0)]
    )

    discount = models.PositiveIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )

    publications = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default="Anwar Publications",
    )

    availability = models.CharField(
        max_length=20, choices=AVAILABILITY_CHOICES, default="pending"
    )

    language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        default="hindi",
    )

    binding_types = models.CharField(
        max_length=20,
        choices=BINDING_CHOICES,
        default="softcover",
    )

    edition = models.CharField(max_length=20, choices=EDITION_CHOICES, default="bulk")

    description = models.TextField()
    summary = models.TextField(null=True, blank=True)

    publication_date = models.DateField()

    # ------------ Auto Fields ------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ------------ Computed Field ------------
    @property
    def sale_price(self):
        """Price after discount"""
        if not self.discount:
            return self.price

        discount_decimal = Decimal(self.discount) / Decimal(100)
        return round(self.price * (1 - discount_decimal), 2)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]
        unique_together = ("author", "title")
