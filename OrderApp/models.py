from django.db import models

# Create your models here.
import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings


class Order(models.Model):
    class Status(models.TextChoices):
        CREATED = "CREATED", "Created"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.CREATED
    )

    currency = models.CharField(max_length=10, default="INR")
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    # Razorpay mapping
    razorpay_order_id = models.CharField(
        max_length=100, blank=True, null=True, db_index=True
    )
    razorpay_payment_id = models.CharField(
        max_length=100, blank=True, null=True, db_index=True
    )
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} | {self.status} | {self.total_amount} {self.currency}"


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey(
        "BookApp.Books", on_delete=models.PROTECT, related_name="order_items"
    )

    # Snapshots (important)
    title_snapshot = models.CharField(max_length=200)
    unit_price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.title_snapshot} x {self.quantity}"
