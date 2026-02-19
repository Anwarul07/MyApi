from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.utils.crypto import constant_time_compare
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Cartitem.models import CartItem
from OrderApp.models import Order, OrderItem
from OrderApp.serializers import OrderSerializer
from OrderApp.clients import get_client
from Apps.permissions import IsAdminOrBuyerOnly

import hmac
import hashlib


class CreateOrderFromCartView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrBuyerOnly]

    @transaction.atomic
    def post(self, request):
        user = request.user

        cart_items = CartItem.objects.filter(user=user).select_related("books")

        if not cart_items.exists():
            return Response(
                {"msg": "Cart is empty", "status": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Calculate total using CartItem.total (already includes discount)
        total_amount = Decimal("0.00")
        for item in cart_items:
            total_amount += Decimal(str(item.total))

        # Create Order (CREATED)
        order = Order.objects.create(
            user=user,
            status=Order.Status.CREATED,
            currency="INR",
            total_amount=total_amount,
        )

        # Create OrderItems snapshot
        order_items = []
        for ci in cart_items:
            unit_price = Decimal(str(ci.sale_price))
            qty = ci.quantity
            line_total = Decimal(str(ci.total))

            order_items.append(
                OrderItem(
                    order=order,
                    book=ci.books,
                    title_snapshot=ci.books.title,
                    unit_price_snapshot=unit_price,
                    quantity=qty,
                    line_total=line_total,
                )
            )
        OrderItem.objects.bulk_create(order_items)

        # Create Razorpay Order (amount in paise)
        amount_paise = int(total_amount * 100)

        client = get_client()
        rp_order = client.order.create(
            {
                "amount": amount_paise,
                "currency": "INR",
                "receipt": str(order.id),
                "payment_capture": 1,  # auto-capture (common)
            }
        )

        order.razorpay_order_id = rp_order.get("id")
        order.save(update_fields=["razorpay_order_id", "updated_at"])

        return Response(
            {
                "msg": "Order created",
                "status": 201,
                "data": {
                    "internal_order": OrderSerializer(order).data,
                    "razorpay": {
                        "key_id": settings.RAZORPAY_KEY_ID,
                        "order_id": order.razorpay_order_id,
                        "amount": amount_paise,
                        "currency": "INR",
                    },
                },
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyRazorpayPaymentView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrBuyerOnly]

    @transaction.atomic
    def post(self, request):
        """
        Client sends:
        - razorpay_order_id
        - razorpay_payment_id
        - razorpay_signature
        (optional) internal_order_id
        """
        user = request.user
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return Response(
                {"msg": "Missing payment fields", "status": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Find order
        try:
            order = Order.objects.select_for_update().get(
                user=user, razorpay_order_id=razorpay_order_id
            )
        except Order.DoesNotExist:
            return Response(
                {"msg": "Order not found", "status": 404},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Idempotency: if already paid, just return
        if order.status == Order.Status.PAID:
            return Response(
                {
                    "msg": "Already paid",
                    "status": 200,
                    "data": OrderSerializer(order).data,
                },
                status=status.HTTP_200_OK,
            )

        # Signature verify: HMAC_SHA256(order_id|payment_id, key_secret)
        payload = f"{razorpay_order_id}|{razorpay_payment_id}".encode("utf-8")
        expected = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode("utf-8"), payload, hashlib.sha256
        ).hexdigest()

        if not constant_time_compare(expected, razorpay_signature):
            order.status = Order.Status.FAILED
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.save(
                update_fields=[
                    "status",
                    "razorpay_payment_id",
                    "razorpay_signature",
                    "updated_at",
                ]
            )

            return Response(
                {"msg": "Signature verification failed", "status": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mark PAID
        order.status = Order.Status.PAID
        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_signature = razorpay_signature
        order.save(
            update_fields=[
                "status",
                "razorpay_payment_id",
                "razorpay_signature",
                "updated_at",
            ]
        )

        # Clear cart ONLY on success
        CartItem.objects.filter(user=user).delete()

        return Response(
            {
                "msg": "Payment verified. Order paid.",
                "status": 200,
                "data": OrderSerializer(order).data,
            },
            status=status.HTTP_200_OK,
        )


class RazorpayWebhookView(APIView):
    """
    Webhook is a backup source-of-truth.
    IMPORTANT: Use raw request.body for signature verification.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
        if not webhook_secret:
            return Response(
                {"msg": "Webhook secret not set", "status": 500}, status=500
            )

        signature = request.headers.get("X-Razorpay-Signature")
        if not signature:
            return Response({"msg": "Missing signature", "status": 400}, status=400)

        body = request.body  # raw bytes

        expected = hmac.new(
            webhook_secret.encode("utf-8"), body, hashlib.sha256
        ).hexdigest()

        if not constant_time_compare(expected, signature):
            return Response(
                {"msg": "Invalid webhook signature", "status": 400}, status=400
            )

        event = request.data.get("event")

        # We mainly care about payment captured / failed
        # Razorpay payload contains entity details; safest is:
        # - get razorpay_order_id from payload
        payload = request.data.get("payload", {})
        order_entity = payload.get("order", {}).get("entity", {})
        payment_entity = payload.get("payment", {}).get("entity", {})

        razorpay_order_id = order_entity.get("id") or payment_entity.get("order_id")
        razorpay_payment_id = payment_entity.get("id")

        if not razorpay_order_id:
            return Response(
                {"msg": "No order id in webhook", "status": 400}, status=400
            )

        # Update order status based on event
        try:
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
        except Order.DoesNotExist:
            return Response({"msg": "Order not found", "status": 200}, status=200)

        # If already PAID, ignore
        if order.status == Order.Status.PAID:
            return Response({"msg": "OK", "status": 200}, status=200)

        if event in ("payment.captured", "order.paid"):
            order.status = Order.Status.PAID
            if razorpay_payment_id:
                order.razorpay_payment_id = razorpay_payment_id
            order.save(update_fields=["status", "razorpay_payment_id", "updated_at"])

            # Cart clearing ideally already done in verify endpoint.
            # But in case verify missed, you can clear by user:
            CartItem.objects.filter(user=order.user).delete()

        elif event in ("payment.failed",):
            order.status = Order.Status.FAILED
            if razorpay_payment_id:
                order.razorpay_payment_id = razorpay_payment_id
            order.save(update_fields=["status", "razorpay_payment_id", "updated_at"])

        return Response({"msg": "OK", "status": 200}, status=200)




class OrderHistoryView(viewsets.ReadOnlyModelViewSet):
    """
    GET /orders/history/        -> list (buyer: own orders, admin: all)
    GET /orders/history/<id>/   -> detail
    """

    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrBuyerOnly]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status"]  # optional: ?status=PAID
    ordering_fields = ["created_at", "total_amount", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user

        qs = Order.objects.prefetch_related("items").select_related("user")

        if user.is_superuser or user.role == "admin":
            return qs

        # buyer can see only own orders
        return qs.filter(user=user)
