from rest_framework import generics, permissions

from .serializers import CreateUserSerializer


class UserView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = (permissions.AllowAny,)
