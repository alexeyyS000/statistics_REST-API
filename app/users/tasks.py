import json

import stripe
from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.db import OperationalError
from django.utils.translation import gettext_lazy as _

from .models import MembershipLevel
from .models import UserMembershipLevel
from .service import UserService

User = get_user_model()


@shared_task(bind=True, max_retries=3)
def send_message(
    self,
    from_email: str | None = None,
    subject: str | None = None,
    body: str | None = None,
    html_email: str | None = None,
    *args: str,
) -> int:
    try:
        email_message = EmailMultiAlternatives(subject, body, from_email, *args)
        if html_email is not None:
            email_message.attach_alternative(html_email, "text/html")
        email_message.send()

    except Exception as err:
        if self.request.retries < self.max_retries:
            self.retry(exc=err, countdown=60)
        else:
            return


class EventHandler:
    def __init__(self):
        self._handlers = {}

    def on(self, event_type: str):
        def wrapper(func):
            self._handlers[event_type] = func

        return wrapper

    def emit(self, event_type, payload):
        """
        calls a function using a dictionary key
        """
        callback = self._handlers.get(event_type)
        if callback is None:
            return
        callback(payload)


stripe_handlers = EventHandler()


@stripe_handlers.on("customer.subscription.created")
def create_subscription(payload):
    customer_id = payload.object.customer
    plan_id = payload.object.plan.product

    try:
        user, membership_level = UserService.create_sub(customer_id=customer_id, plan_id=plan_id)

    except (MembershipLevel.DoesNotExist, UserMembershipLevel.DoesNotExist, User.DoesNotExist):
        return

    # send_message.delay(
    #     None,
    #     "subscription issued",
    #     f"subscription by plan {membership_level.type} issued",
    #     None,
    #     [
    #         user.email,
    #     ],
    # )


@stripe_handlers.on("customer.subscription.deleted")
def delete_subscription(payload):
    customer_id = payload.object.customer
    plan_id = payload.object.plan.product

    try:
        user, membership_level = UserService.cancel_sub(customer_id=customer_id, plan_id=plan_id)

    except (MembershipLevel.DoesNotExist, UserMembershipLevel.DoesNotExist, User.DoesNotExist):
        return

    # send_message.delay(
    #     None,
    #     "subscription canceled",
    #     f"your subscription by plan {membership_level.type} canceled",
    #     None,
    #     [
    #         user.email,
    #     ],
    # )


@stripe_handlers.on("customer.subscription.updated")
def extend_subscription(payload):
    if payload.object.cancel_at is None:  # and payload.previous_attributes.status != 'incomplete':
        customer_id = payload.object.customer
        plan_id = payload.object.plan.product

        try:
            user, membership_level = UserService.update_sub(customer_id=customer_id, plan_id=plan_id)

        except (MembershipLevel.DoesNotExist, UserMembershipLevel.DoesNotExist, User.DoesNotExist):
            return
        # send_message.delay(
        #     None,
        #     "subscription extended",
        #     f"subscription extended by plan: {membership_level.type}",
        #     None,
        #     [
        #         user.email,
        #     ],
        # )


@shared_task(
    name="distribution_task",
    autoretry_for=(OperationalError,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def distribution_task(event_type, payload):
    try:
        json_data = json.loads(payload)
    except json.JSONDecodeError:
        return

    try:
        payload = stripe.Event.construct_from(
            json_data,
            stripe.api_key,
        )
    except (ValueError, stripe.error.SignatureVerificationError) as ex:
        return

    stripe_handlers.emit(event_type, payload.data)


@shared_task(ignore_result=False)
def create_stripe_customer(user_email: str) -> str:
    customer = stripe.Customer.create(
        email=user_email,
    )
    return customer.id
