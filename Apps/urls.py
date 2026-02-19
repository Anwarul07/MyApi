from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from Apps.views import (
    SendOTPView,
    UserRegisterView,
    LoginView,
    LogoutView,
    LogoutAllView,
    SendLoginOTPView,
    SendPasswordUpdateOTPView,
    UpdatePasswordConfirmView,
    SendForgetPasswordOTPView,
    ForgetPasswordConfirmView,
    SendUserDeleteOTPView,
    DeleteUserConfirmView,
)

app_name = "apps"

urlpatterns = [
    # -------- Auth / OTP --------
    path("register-confirm/", UserRegisterView.as_view(), name="register"),
    path("otp-registration/", SendOTPView.as_view(), name="send-otp"),
    path("otp-login/", SendLoginOTPView.as_view(), name="login-send-otp"),
    path("login-confirm/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("logout-all/", LogoutAllView.as_view(), name="logout-all"),
    # -------- JWT --------
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    # -------- Password --------
    path("pwd-update-otp/", SendPasswordUpdateOTPView.as_view(), name="pwd-update-otp"),
    path(
        "password-update/",
        UpdatePasswordConfirmView.as_view(),
        name="pwd-update-confirm",
    ),
    path("forget-pwd-otp/", SendForgetPasswordOTPView.as_view(), name="forget-pwd-otp"),
    path(
        "forget-password/",
        ForgetPasswordConfirmView.as_view(),
        name="forget-pwd-confirm",
    ),
    # -------- Account --------
    path("otp/delete-user/", SendUserDeleteOTPView.as_view(), name="delete-user-otp"),
    path("delete-user/", DeleteUserConfirmView.as_view(), name="delete-user-confirm"),
]
