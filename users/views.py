from django.contrib.auth.models import Group
from django.db import IntegrityError

from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import generics, permissions
from rest_framework import status

from .permissions import IsOwnerOrReadOnly
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
        try:
            serializer.is_valid(raise_exception=True)
        except:
            msg = {'detail': 'Unable to log in with provided credentials'}
            return Response(msg, status=status.HTTP_401_UNAUTHORIZED)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                'token': token.key,
                'id': user.id,
                'ful_name': user.full_name,
                'email': user.email
            }
        )


class UserView(generics.ListCreateAPIView):
    """
    Service to create new users.
    Need authentication to list user

    :accepted methods:
    GET
    POST
    """
    serializer_class = CreateUserSerializer
    permission_classes = (permissions.AllowAny,)
    allowed_methods = ('GET', 'POST',)
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            dict(serializer.data, token=str(user.auth_token)),
            status=status.HTTP_201_CREATED, headers=headers
        )

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            message = {
                "detail": "Authentication credentials were not provided."
            }
            return Response(
                message,
                status=status.HTTP_403_FORBIDDEN,
            )
        return self.list(request, *args, **kwargs)


class UserGetUpdateView(generics.RetrieveUpdateAPIView):
    """
    Service to update users.
    PUT Method is used to update all required fields. Will responde in case
    some is missing
    PATCH Method is used to update any field, will not response in case
    some required fill is missing

    :accepted methods:
    GET =  Dont need authentication
    PUT = Need authentication
    PATCH = Need authentication
    """
    serializer_class = UserSerializers
    permission_classes = (IsOwnerOrReadOnly,)
    allowed_methods = ('GET', 'PUT', 'PATCH')
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'user': request.user}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            dict(serializer.data, token=str(user.auth_token)),
            status=status.HTTP_201_CREATED, headers=headers
        )


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
        try:
            serializer.save()
        except IntegrityError as e:
            error = {'detail': str(e)}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
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
        try:
            serializer.save()
        except IntegrityError as e:
            error = {'detail': str(e)}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserDetailView(generics.RetrieveUpdateAPIView):
    '''
        Service to Retrive and Update user
        :accepted methods:
            POST
            GET
    '''
    serializer_class = UserSerializers
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Veterinarian.objects.all()
    allowed_methods = ('GET', 'POST')
