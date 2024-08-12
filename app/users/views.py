# from django.conf import settings
# from django.contrib.auth import authenticate
import datetime

import stripe
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetView
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect

# from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect

from .forms import LoginForm
from .forms import TariffPlanForm
from .forms import UserCreationForm
from .models import Token
from .models import UserMembershipLevel
from .tasks import create_stripe_customer
from .tasks import distribution_task
from .utils.general import CustomPasswordResetForm
from .utils.general import email_authenticate
from .utils.token import JWT

User = get_user_model()


class RegisterUserView(View):
    template_name = "registration/register.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {"form": UserCreationForm}
        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def post(self, request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            password = form.cleaned_data.get("password1")
            email = form.cleaned_data.get("email")
            user = email_authenticate(email=email, password=password)
            result = create_stripe_customer.delay(email)
            stripe_customer_id = result.get()
            user.customer_id = stripe_customer_id
            user.save()
            login(request, user)
            return redirect("home")
        context = {"form": form}
        return render(request, self.template_name, context)


class ProfileView(LoginRequiredMixin, View):
    template_name = "users/profile.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {"form": AuthenticationForm}
        return render(request, self.template_name, context)


class LoginView(View):
    template_name = "registration/login.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {"form": LoginForm}
        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def post(self, request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
        form = LoginForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get("password")
            email = form.cleaned_data.get("email")
            user = email_authenticate(email=email, password=password)
            login(request, user)
            return redirect("home")
        context = {"form": form}
        return render(request, self.template_name, context)


class CustomPasswordResetView(PasswordResetView):
    email_template_name = "emails/password_reset_email.html"
    success_url = reverse_lazy("users:password_reset_done")
    form_class = CustomPasswordResetForm


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy("users:password_reset_complete")


class GetToken(LoginRequiredMixin, View):
    template_name = "users/token.html"

    def post(self, request: HttpRequest) -> HttpResponse:
        user = User.objects.get(id=request.user.id)
        old_token = Token.objects.filter(user__id=request.user.id, deleted=None).first()
        if old_token:
            old_token.deleted = datetime.datetime.now(datetime.timezone.utc)
            old_token.save()

        token = Token.objects.create(user=user, deleted=None)
        payload = {
            "user_id": user.id,
            "token_id": token.id,
        }

        token = JWT.encode(
            payload,
        )
        context = {"token": token, "is_token_exist": True}
        return render(request, self.template_name, context)

    def get(self, request: HttpRequest) -> HttpResponse:
        is_token_exist = Token.objects.filter(user__id=request.user.id, deleted=None).exists()
        context = {"is_token_exist": is_token_exist}
        return render(request, self.template_name, context)


@csrf_exempt
def payment_webhook(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    endpoint_secret = "whsec_mcZ8y9DQeLM73aQ5hnPuwqiNrlfBbdu6"

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)

    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    distribution_task.delay(event_type=event.type, payload=payload)
    return HttpResponse(status=200)


def open_customer_portal(request: HttpRequest):
    customer = stripe.Customer.retrieve(request.user.customer_id)
    portal_session = stripe.billing_portal.Session.create(customer=customer.id, return_url="http://127.0.0.1:8000/")
    return redirect(portal_session.url)


class PaymentView(LoginRequiredMixin, View):
    template_name = "users/result_template.html"
    success_url = "users/payment_success"
    cancel_url = "users/payment_failed"

    def get(self, request):
        form = TariffPlanForm()
        subscription = UserMembershipLevel.objects.filter(user=request.user, ended__isnull=True).first()
        if subscription is None:
            subscriber = False
        else:
            subscriber = True
        return render(request, self.template_name, {"form": form, "subscriber": subscriber})

    def post(self, request):
        form = TariffPlanForm(request.POST)
        if form.is_valid():
            selected_choice = form.cleaned_data["choices"]

            product = stripe.Product.retrieve(selected_choice)
            prices = stripe.Price.list(product=product)

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": prices["data"][0].id,
                        "quantity": 1,
                    },
                ],
                mode="subscription",
                customer=request.user.customer_id,
                success_url=f"http://{request.get_host()}/{self.success_url}",
                cancel_url=f"http://{request.get_host()}/{self.cancel_url}",
            )

            return redirect(checkout_session.url, code=303)

        else:
            return render(request, self.template_name, {"form": form})


class PaymentSuccess(View):
    template_name = "users/payment_success.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name)


class PaymentFailed(View):
    template_name = "users/payment_failed.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name)
