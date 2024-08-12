from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import render
from users.models import RequestLog
from users.models import Token
from users.utils.token import JWT

from .utils.errors import BaseHttpError
from .utils.general import check_string

User = get_user_model()


class ErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if not settings.DEBUG:
            if isinstance(exception, BaseHttpError):
                return render(
                    request,
                    "errors/base.html",
                    {"status": exception.status, "message": exception.message, "error_name": exception.error_name},
                )
            return HttpResponse("Error processing the request.", status=HTTPStatus.INTERNAL_SERVER_ERROR)


class AuthorizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")

        if "/api/" in request.path:
            if not token:
                return HttpResponse("failed authorization error", status=HTTPStatus.UNAUTHORIZED)
            payload = JWT.decode(token)
            token = Token.objects.filter(id=payload["token_id"]).first()
            if token and token.deleted is None:
                user = User.objects.with_requests_left().get(id=payload["user_id"])
                if user.requests_left < 1:
                    return HttpResponse("ftoo many requests", status=HTTPStatus.TOO_MANY_REQUESTS)
            else:
                return HttpResponse("failed authorization error", status=HTTPStatus.UNAUTHORIZED)
        response = self.get_response(request)
        return response


class RequestLoggingMiddleware:
    def __init__(self, get_response):  # считаю только запросы с токеном
        self.get_response = get_response

    def __call__(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
        response = self.get_response(request)
        if token:
            payload = JWT.decode(token)
            if check_string(request.path, settings.COUNTABLE_URLS):
                user = User.objects.get(id=payload["user_id"])
                if response.status_code == 200:
                    RequestLog(url=request.path, user=user, countable=True).save()

        return response
