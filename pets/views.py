from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView)
from rest_framework import permissions

from TapVet import messages
from users.models import User

from .models import Pet, PetType
from .serializers import PetSerializer, PetTypeSerializer
from TapVet.permissions import IsOwnerOrReadOnly


class PetsListCreateView(ListCreateAPIView):
    """
    Service to create new and list pets.
    Need authentication

    :accepted methods:
    GET = Retrieve pet list, need admin status
    POST = Create a Pet
    """
    serializer_class = PetSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly,)
    queryset = Pet.objects.all().select_related('user', 'pet_type')

    def create(self, request, *args, **kwargs):
        if not request.user.has_perm('pets.add_pet'):
            return Response(
                {
                    'detail': messages.pet_no_pets
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer = self.serializer_class(
            data=request.data,
            context={'user': request.user}
        )
        serializer.is_valid(raise_exception=True)
        try:
            if 'image' in request.data:
                serializer.save(image=request.data['image'])
            else:
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
                "detail": messages.admin_required
            }
            return Response(
                message,
                status=status.HTTP_403_FORBIDDEN,
            )

        return self.list(request, *args, **kwargs)


class PetRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    serializer_class = PetSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
    queryset = Pet.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer, request.data)
        return Response(serializer.data)

    def perform_update(self, serializer, data):
        if 'image' in data:
            serializer.save(image=data['image'])
        else:
            serializer.save()


class PetListByUser(ListAPIView):
    serializer_class = PetSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """
        Get the list of pets for the user pk
        """
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        queryset = Pet.objects.filter(user=user)
        return queryset


class PetTypeListView(ListAPIView):
    serializer_class = PetTypeSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = PetType.objects.all()
