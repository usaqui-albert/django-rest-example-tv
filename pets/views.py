from django.db import IntegrityError
from django.core.exceptions import ValidationError

from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework import permissions

from .models import Pet
from .serializers import PetSerializer
from .permissions import IsOwnerReadOnly


class PetsListCreateView(ListCreateAPIView):
    """
    Service to create new and list pets.
    Need authentication

    :accepted methods:
    GET = Retrive pet list, need admin status
    POST = Create a Pet
    """
    serializer_class = PetSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerReadOnly,)
    queryset = Pet.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'user': request.user}
        )
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except (IntegrityError, ValueError, ValidationError) as e:
            error = {'detail': str(e)}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            message = {
                "detail": "Admin level is needed for this action."
            }
            return Response(
                message,
                status=status.HTTP_403_FORBIDDEN,
            )

        return self.list(request, *args, **kwargs)
