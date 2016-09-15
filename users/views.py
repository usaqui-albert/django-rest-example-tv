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
    throttle_classes = ()
    permission_classes = ()

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
    serializer_class = CreateUserSerializer
    permission_classes = (permissions.AllowAny,)


class GroupsListView(generics.ListAPIView):
    serializer_class = GroupsSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Group.objects.all()
    allowed_methods = ('GET',)


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializers
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    allowed_methods = ('GET',)


class BreederListCreateView(generics.ListCreateAPIView):
    serializer_class = BreederSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Breeder.objects.all()
    allowed_methods = ('GET', 'POST')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(id=1)
        self.perform_create(serializer, user=user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, user):
        serializer.save(user=user)


class VeterinarianListCreateView(generics.ListCreateAPIView):
    serializer_class = VeterinarianSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Veterinarian.objects.all()
    allowed_methods = ('GET', 'POST')
