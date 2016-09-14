from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import generics, permissions

from .models import User
from .serializers import CreateUserSerializer, UserSerializers


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


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializers
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    allowed_methods = ('get',)
