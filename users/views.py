from rest_framework import generics, permissions

from .serializers import CreateUserSerializer, UserSerializer
from .models import User


class UserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (permissions.AllowAny,)
