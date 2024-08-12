from django_filters import rest_framework as filters

from .models import Novelty
from .models import Poll


class PollFilter(filters.FilterSet):
    # title = filters.CharFilter(lookup_expr='icontains')
    # created_at = filters.DateTimeFilter()

    class Meta:
        model = Poll
        fields = "__all__"


class NoveltyFilter(filters.FilterSet):
    answers = filters.CharFilter(lookup_expr="icontains")
    # created_at = filters.DateTimeFilter()

    class Meta:
        model = Novelty
        fields = "__all__"
