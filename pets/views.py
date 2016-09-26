from django.db import IntegrityError

from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView

from .models import Pet
from .serializers import PetSerializer
from .permissions import IsOwnerOrReadOnly


class PetsListCreateView(ListCreateAPIView):
    """
    Service to create new and list pets.
    Need authentication

    :accepted methods:
    GET = Retrive pet list, need admin status
    POST = Create a Pet
    """
    serializer_class = PetSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    queryset = Pet.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'user': request.user}
        )
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except (IntegrityError, ValueError) as e:
            error = {'detail': str(e)}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)
