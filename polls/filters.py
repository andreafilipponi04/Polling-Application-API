from django_filters import rest_framework as filters

from .models import Poll


class PollFilter(filters.FilterSet):
    question = filters.CharFilter(
        field_name='question',
        lookup_expr='icontains'
    )
    is_active = filters.BooleanFilter(
        field_name='is_active'
    )
    created_by = filters.CharFilter(
        field_name='created_by__username',
        lookup_expr='icontains'
    )

    class Meta:
        model = Poll
        fields = ['question', 'is_active', 'created_by']