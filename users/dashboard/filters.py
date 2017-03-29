from django_filters.rest_framework import FilterSet, BooleanFilter

from ..models import User


class UserFilter(FilterSet):
    locked = BooleanFilter(name='veterinarian__locked')
    verified = BooleanFilter(name='veterinarian__verified')

    class Meta:
        model = User
        fields = [
            'username', 'email', 'full_name', 'is_active', 'groups',
            'veterinarian__verified', 'veterinarian__locked'
        ]
