from django.contrib.auth.models import Group

from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import generics, permissions
from rest_framework import status

from .models import User, Breeder, Veterinarian
from .serializers import (
    CreateUserSerializer, UserSerializers, VeterinarianSerializer,
    BreederSerializer, GroupsSerializer
)


class UserAuth(ObtainAuthToken):
    """
    Service to authenticate users.

    :accepted methods:
        POST
    """
    allowed_methods = ('POST',)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                'token': token.key,
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email
            }
        )


class UserCreateView(generics.CreateAPIView):
    """
    Service to create new users.

    :accepted methods:
        POST
    """
    serializer_class = CreateUserSerializer
    permission_classes = (permissions.AllowAny,)
    allowed_methods = ('POST',)


class GroupsListView(generics.ListAPIView):
    """
    Service to list users groups.

    :accepted methods:
        GET
    """
    serializer_class = GroupsSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Group.objects.all()
    allowed_methods = ('GET',)


class UserListView(generics.ListAPIView):
    """
    Service to list users.

    :accepted methods:
        GET
    """
    serializer_class = UserSerializers
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    allowed_methods = ('GET',)


class BreederListCreateView(generics.ListCreateAPIView):
    """
    Service to create and list Breeder users. Need and authenticated user

    :accepted methods:
        POST
        GET
    """
    serializer_class = BreederSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Breeder.objects.all()
    allowed_methods = ('GET', 'POST')

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'user': request.user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class VeterinarianListCreateView(generics.ListCreateAPIView):
    """
    Service to create and list Veterinarians users. Need and authenticated user

    :accepted methods:
        POST
        GET
    """
    serializer_class = VeterinarianSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Veterinarian.objects.all()
    allowed_methods = ('GET', 'POST')

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'user': request.user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)
