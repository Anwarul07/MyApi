from rest_framework import serializers
from OrderApp.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "book",
            "title_snapshot",
            "unit_price_snapshot",
            "quantity",
            "line_total",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "currency",
            "total_amount",
            "razorpay_order_id",
            "razorpay_payment_id",
            "created_at",
            "updated_at",
            "items",
        ]
