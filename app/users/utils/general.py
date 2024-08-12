import uuid

from django.contrib.auth.forms import PasswordResetForm
from django.core.cache import cache
from django.http import HttpRequest
from django.template import loader
from django.urls import reverse_lazy

from ..models import User
from ..tasks import send_message


def email_authenticate(email: str, password: str) -> User | None:
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None
    else:
        if user.check_password(password):
            return user
    return None


def generate_confirm_link(request: HttpRequest, token: str) -> str:
    confirm_link = request.build_absolute_uri(reverse_lazy("users:register_confirm", kwargs={"token": token}))
    return confirm_link


def set_verification_token(token: str, timeout: int, temlpale: str, **kwargs: str) -> bool:
    redis_key = temlpale.format(token=token)
    set_cache = cache.set(redis_key, kwargs, timeout=timeout)
    return set_cache


def get_cache(redis_key: str) -> dict:
    get_cache = cache.get(redis_key) or {}
    return get_cache


def generate_token() -> str:
    return uuid.uuid4().hex


# class
class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        """
        Overriding a function send_mail() in a class PasswordResetForm
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
        else:
            html_email = None
        send_message.delay(
            from_email,
            subject,
            body,
            html_email,
            [
                to_email,
            ],
        )
