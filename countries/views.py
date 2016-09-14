from rest_framework import permissions
from rest_framework.generics import ListAPIView
from django.db.models.query import QuerySet

from .models import State
from .serializers import StateSerializer


class StateList(ListAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
            """
            Get the list of items for this view.
            This must be an iterable, and may be a queryset.
            Defaults to using `self.queryset`.

            This method should always be used rather than accessing
            `self.queryset` directly, as `self.queryset` gets evaluated only
            once, and those results are cached for all subsequent requests.

            You may want to override this if you need to provide different
            querysets depending on the incoming request.

            (Eg. return a list of items that is specific to the user)
            """
            assert self.queryset is not None, (
                "'%s' should either include a `queryset` attribute, "
                "or override the `get_queryset()` method."
                % self.__class__.__name__
            )

            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                # Ensure queryset is re-evaluated on each request.
                queryset = queryset.all()
            queryset = queryset.filter(country=self.kwargs['pk'])
            return queryset
