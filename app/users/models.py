import datetime

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.db import models
from django.db.models import Case
from django.db.models import Count
from django.db.models import F
from django.db.models import Value
from django.db.models import When
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _


class UserManager(UserManager):
    def with_requests_left(self):
        return self.annotate(
            requests_left=Coalesce(F("membershiplevels__membership_level__requests_number"), Value(50))
            - Count(Case(When(requestlogs__countable=True, requestlogs__created__date=datetime.date.today(), then=1)))
        )


class User(AbstractUser):
    birthday = models.DateField(null=True)
    updated = models.DateTimeField(auto_now=True)
    email = models.EmailField(_("email address"), blank=True, unique=True)
    username = None
    customer_id = models.CharField(null=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()


class MembershipLevel(models.Model):
    type = models.CharField(null=False)
    requests_number = models.IntegerField(null=False)
    stripe_plan_id = models.CharField(null=False)


class RequestLog(models.Model):
    user = models.ForeignKey(User, related_name="requestlogs", on_delete=models.SET_NULL, null=True)
    url = models.CharField(null=False)
    countable = models.BooleanField(null=False)
    created = models.DateTimeField(auto_now_add=True)


class UserMembershipLevel(models.Model):
    user = models.ForeignKey(User, related_name="membershiplevels", on_delete=models.CASCADE)
    membership_level = models.ForeignKey(MembershipLevel, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    ended = models.DateTimeField(null=True, default=None)


class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    deleted = models.DateTimeField(null=True, default=None)
