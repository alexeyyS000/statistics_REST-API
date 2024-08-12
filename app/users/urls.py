from django.urls import include
from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    path("signup/", views.RegisterUserView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path(
        "reset/<uidb64>/<token>/",
        views.CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("password_reset/", views.CustomPasswordResetView.as_view(), name="password_reset"),
    path("", include("django.contrib.auth.urls")),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("token/", views.GetToken.as_view(), name="get_token"),
    path("create_payment/", views.PaymentView.as_view(), name="payment"),
    path("payment_webhook/", views.payment_webhook, name="payment_webhook"),
    path("open_customer_portal/", views.open_customer_portal, name="open_customer_portal"),
    path("payment_success/", views.PaymentSuccess.as_view(), name="payment_success"),
    path("payment_failed/", views.PaymentFailed.as_view(), name="payment_failed"),
]
