from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework import status

from TapVet import messages
from TapVet.pagination import StandardPagination
from users.serializers import UserLoginSerializer
from users.models import User

from .serializers import AdminAuthTokenSerializer, AdminUserSerializer


class AdminAuth(ObtainAuthToken):
    """
    Service to authenticate Admins.

    :accepted methods:
        POST
    """
    allowed_methods = ('POST',)
    serializer_class = AdminAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response(
                messages.bad_login, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.validated_data['user']
        token = Token.objects.filter(user=user).first()
        if not token:
            return Response(
                messages.inactive, status=status.HTTP_403_FORBIDDEN)
        serializer = UserLoginSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminUsersListView(ListAPIView):
    pagination_class = StandardPagination
    queryset = User.objects.all()
    permission_classes = (IsAdminUser,)
    serializer_class = AdminUserSerializer
