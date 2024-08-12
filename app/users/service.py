import datetime

from django.contrib.auth import get_user_model

from .models import MembershipLevel
from .models import UserMembershipLevel

User = get_user_model()


class UserService:
    def cancel_sub(customer_id, plan_id):
        user = User.objects.prefetch_related("membershiplevels").get(customer_id=customer_id)

        plan = MembershipLevel.objects.get(stripe_plan_id=plan_id)

        current_membership = user.membershiplevels.get(membership_level=plan, ended__isnull=True)

        current_membership.ended = datetime.datetime.now(datetime.timezone.utc)
        current_membership.save()

    def update_sub(customer_id, plan_id):
        user = User.objects.prefetch_related("membershiplevels").get(customer_id=customer_id)
        current_membership = user.membershiplevels.filter(ended__isnull=True)
        current_membership.update(ended=datetime.datetime.now(datetime.timezone.utc))
        membership_level = MembershipLevel.objects.get(stripe_plan_id=plan_id)
        UserMembershipLevel.objects.create(user=user, membership_level=membership_level)
        return user, membership_level

    def create_sub(customer_id, plan_id):
        user = User.objects.prefetch_related("membershiplevels").get(customer_id=customer_id)

        membership_level = MembershipLevel.objects.get(stripe_plan_id=plan_id)

        current_membership = user.membershiplevels.filter(membership_level=membership_level, ended__isnull=True).first()

        if current_membership is None:
            UserMembershipLevel.objects.create(user=user, membership_level=membership_level)
        else:
            current_membership.ended = datetime.datetime.now(datetime.timezone.utc)
            current_membership.save()
            UserMembershipLevel.objects.create(user=user, membership_level=membership_level)

        return user, membership_level
