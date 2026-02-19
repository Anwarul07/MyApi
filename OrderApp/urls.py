from django.urls import path, include
from rest_framework.routers import DefaultRouter

from OrderApp.views import (
    CreateOrderFromCartView,
    VerifyRazorpayPaymentView,
    RazorpayWebhookView,
    OrderHistoryView,
)


router = DefaultRouter()
router.register("history", OrderHistoryView, basename="order-history")

urlpatterns = [
    # payment flow
    path(
        "create-from-cart/", CreateOrderFromCartView.as_view(), name="create-from-cart"
    ),
    path("verify-payment/", VerifyRazorpayPaymentView.as_view(), name="verify-payment"),
    path("razorpay-webhook/", RazorpayWebhookView.as_view(), name="razorpay-webhook"),
    # history endpoints
    path("", include(router.urls)),
]
