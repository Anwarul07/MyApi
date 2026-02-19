import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from BookApp.models import Books
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

# ---Cartitem user Model ---


class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carts"
    )
    books = models.ForeignKey(
        "BookApp.Books", on_delete=models.CASCADE, related_name="cart_items"
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "books")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user.username} → {self.books.title}"

    # --- Calculated Sale Price (single book price after discount)
    @property
    def sale_price(self):
        price = Decimal(self.books.price)
        discount = Decimal(self.books.discount or 0)

        if discount > 0:
            discount_rate = discount / Decimal(100)
            return round(price * (Decimal(1) - discount_rate), 2)

        return round(price, 2)

    # --- Total = sale price × quantity
    @property
    def total(self):
        return round(self.sale_price * self.quantity, 2)
