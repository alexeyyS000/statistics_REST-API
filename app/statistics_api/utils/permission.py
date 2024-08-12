from django.contrib.auth import get_user_model
from rest_framework import permissions
from users.models import Token
from users.utils.token import JWT

User = get_user_model()


class CustomStatisticAuthorization(permissions.BasePermission):  # на уровень приложения
    def has_permission(self, request, view):
        authorization_header = request.META.get("HTTP_AUTHORIZATION")

        if not authorization_header:
            return False

        payload = JWT.decode(authorization_header)
        token = Token.objects.filter(id=payload["token_id"]).first()  # jti

        if (
            token
            and token.deleted is None
            and User.objects.with_requests_left().get(id=payload["user_id"]).requests_left > 0
        ):
            return True

        return False


class CustomReuqestsLeftAuthorization(permissions.BasePermission):
    def has_permission(self, request, view):
        authorization_header = request.META.get("HTTP_AUTHORIZATION")
        payload = JWT.decode(authorization_header)
        token = Token.objects.filter(id=payload["token_id"]).first()
        if token and token.deleted:
            return False
        if not authorization_header:
            return False

        return True
