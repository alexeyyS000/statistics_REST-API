from rest_framework import serializers

from .models import Novelty
from .models import Poll
from .models import PollAnswer


class PollsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = "__all__"


class PollAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollAnswer
        fields = "__all__"


class PollDetailSerializer(serializers.ModelSerializer):
    answer = PollAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Poll
        fields = "__all__"


class NoveltySerializer(serializers.ModelSerializer):
    class Meta:
        model = Novelty
        fields = "__all__"


# class SessionTokenObtainSerializer(TokenObtainSerializer):
#     def validate(self, attrs):
#         data = {}

#         user = self.context["request"].user
#
#         if user and user.is_authenticated:
#             refresh = RefreshToken.for_user(user)
#             data["refresh"] = str(refresh)
#             data["access"] = str(refresh.access_token)
#         else:
#             msg = "User is not authenticated."
#             raise serializers.ValidationError(msg)

#         return data
