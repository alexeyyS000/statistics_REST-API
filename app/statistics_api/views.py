from http import HTTPStatus

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from statistics_api.utils.permission import CustomReuqestsLeftAuthorization
from statistics_api.utils.permission import CustomStatisticAuthorization
from users.utils.token import JWT

from .filters import NoveltyFilter
from .filters import PollFilter
from .models import Novelty
from .models import Poll
from .serializers import NoveltySerializer
from .serializers import PollDetailSerializer
from .serializers import PollsSerializer

User = get_user_model()

stripe.api_key = settings.STRIPE_SECRET_KEY


class AllPollsView(generics.ListAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollsSerializer
    permission_classes = [CustomStatisticAuthorization]
    filterset_class = PollFilter
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    ordering_fields = ["title"]
    ordering = ["title"]  # Поле по умолчанию для сортировки


class PollDetail(APIView):
    permission_classes = [CustomStatisticAuthorization]

    def get(self, request, poll_id: int):
        try:
            poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            return HttpResponse("Not Found", status=HTTPStatus.NOT_FOUND)
        serializer = PollDetailSerializer(poll, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AllNoveltiesView(generics.ListAPIView):
    queryset = Novelty.objects.all()
    serializer_class = NoveltySerializer
    permission_classes = [CustomStatisticAuthorization]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = NoveltyFilter


class NoveltyDetail(APIView):
    permission_classes = [CustomStatisticAuthorization]

    def get(self, request, novelty_id: int):
        try:
            novelty = Novelty.objects.get(id=novelty_id)
        except Novelty.DoesNotExist:
            return HttpResponse("Not Found", status=HTTPStatus.NOT_FOUND)
        serializer = NoveltySerializer(novelty, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RequestsLeft(APIView):
    permission_classes = [CustomReuqestsLeftAuthorization]

    def get(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
        if token:
            payload = JWT.decode(token)
            user = User.objects.with_requests_left().get(id=payload["user_id"])
        else:
            user = request.user if request.user.is_authenticated else None
        if user is None:
            return HttpResponse("failed authorization error", status=HTTPStatus.UNAUTHORIZED)
        return Response({"requests_left": user.requests_left}, status=status.HTTP_200_OK)
