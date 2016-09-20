from rest_framework import permissions
from rest_framework.generics import ListAPIView
from django.db.models.query import QuerySet

from .models import State, Country
from .serializers import StateSerializer, CountriesSerializer


class StateListView(ListAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                # Ensure queryset is re-evaluated on each request.
                queryset = queryset.all()
            queryset = queryset.filter(country=self.kwargs['pk'])
            return queryset


class CountryListView(ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountriesSerializer
    permission_classes = (permissions.AllowAny,)
