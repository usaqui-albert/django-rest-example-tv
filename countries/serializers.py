from rest_framework import serializers

from .models import Country, State


class CountriesSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'name', 'code')
        read_only_fields = ('id', 'name', 'code')


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ('id', 'name', 'country')
