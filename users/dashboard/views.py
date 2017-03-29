from django.shortcuts import get_object_or_404
from django.http import Http404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.views import APIView
from rest_framework.generics import (
    ListAPIView, RetrieveUpdateAPIView, GenericAPIView
)

from django_filters.rest_framework import DjangoFilterBackend

from TapVet import messages
from TapVet.pagination import StandardPagination
from users.serializers import UserLoginSerializer, VeterinarianSerializer
from users.models import User, Veterinarian
from pets.views import PetListByUser
from posts.models import Post

from .serializers import (
    AdminAuthTokenSerializer, AdminUserSerializer, AdminVerificationSerializer,
    AdminUserUpdateSerializer
)
from users.tasks import vet_verify_mail

from .filters import UserFilter


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
    '''
    View for the admin dashboard. This view will paginate users by 20 per
    page.

    Will allow to change the amount of users per page by sending 'page_size'
    queryparam

    ORDERING FIELDS:
        * is_active
        * username
        * email
        * full_name
        * created_at

    SEARCH FIELDS:
        * username
        * email
        * full_name
        * is_active
        * groups
        * veterinarian__verified
        * veterinarian__locked
        * locked
        * verified

    EXAMPLES
    * ORDERING:
        -- api/v1/dashboard/users?ordering=username
        -- api/v1/dashboard/users?ordering=-username (Reverse of the above)
        -- api/v1/dashboard/users?ordering=is_active,username
    * SEARCHING:
        -- api/v1/dashboard/users?category=username&is_active=True
        -- api/v1/dashboard/users?veterinarian__verified=True
    * PAGE SIZE:
        -- api/v1/dashboard/users?page_size=40

    '''
    pagination_class = StandardPagination
    queryset = User.objects.all().select_related(
        'image',
        'veterinarian__country', 'veterinarian__state',
        'breeder__country', 'breeder__state'
    )
    permission_classes = (IsAdminUser,)
    serializer_class = AdminUserSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    search_fields = ('username', 'full_name', 'email')
    filter_fields = (
        'username', 'email', 'full_name', 'is_active', 'groups',
        'veterinarian__verified', 'veterinarian__locked'
    )
    ordering_fields = (
        'is_active', 'username', 'email', 'full_name', 'created_at'
    )
    filter_class = UserFilter


class AdminUserDetailView(RetrieveUpdateAPIView):
    pagination_class = StandardPagination
    permission_classes = (IsAdminUser,)
    serializer_class = AdminUserSerializer
    queryset = User.objects.all().select_related(
        'image',
        'veterinarian__country', 'veterinarian__state',
        'breeder__country', 'breeder__state', 'groups'
    )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = AdminUserUpdateSerializer(
            instance,
            data=request.data,
            partial=partial,
            context={
                'user': request.user,
                'request': request
            }
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class AdminPetView(PetListByUser):
    permission_classes = (IsAdminUser,)


class AdminUserDeactive(APIView):
    '''
    Service to manage the user sessions.
    METHODS
    POST
    * Create the auth token for any user
    DELETE
    * Delete the auth token for any user except super admin
    '''
    allowed_methods = ('POST', 'DELETE')
    permission_classes = (IsAdminUser,)

    @staticmethod
    def post(request, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get('pk', None))
        user.is_active = True
        user.save()
        if hasattr(user, 'auth_token'):
            return Response(status=status.HTTP_200_OK)
        else:
            Token.objects.create(user=user)
            return Response(status=status.HTTP_201_CREATED)

    @staticmethod
    def delete(request, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get('pk', None))
        if not user.is_superuser:
            user.is_active = False
            user.save()
            Token.objects.filter(user=user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class AdminVetVerificationView(GenericAPIView):
    permission_classes = (IsAdminUser,)
    serializer_class = AdminVerificationSerializer
    allowed_methods = ('PATCH',)

    def patch(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid()
        vet = Veterinarian.objects.filter(
            user=kwargs['pk']
        ).first()
        if vet:
            vet.verified = serializer.validated_data['verified']
            vet.locked = serializer.validated_data['locked']
            vet.save()
            vet_serializer = VeterinarianSerializer(vet)
            if serializer.validated_data['verified']:
                vet_verify_mail(vet.user, vet.veterinarian_type)
                Post.objects.filter(user=vet.user).update(visible_by_vet=True)
            return Response(
                vet_serializer.data,
                status=status.HTTP_202_ACCEPTED
            )
        raise Http404()
