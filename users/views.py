from operator import xor
from push_notifications.models import APNSDevice, GCMDevice

from django.db import IntegrityError
from django.db.models import Count, Value, Case, When, BooleanField
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from django.http import Http404

from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import permissions
from rest_framework.generics import (
    ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView,
    GenericAPIView
)
from rest_framework.views import APIView
from rest_framework import status

from TapVet import messages
from TapVet.pagination import StandardPagination
from TapVet.permissions import IsOwnerOrReadOnly

from .models import User, Breeder, Veterinarian, AreaInterest, VerificationCode

from .serializers import (
    CreateUserSerializer, UserSerializers, VeterinarianSerializer,
    BreederSerializer, GroupsSerializer, AreaInterestSerializer,
    UserUpdateSerializer, ReferFriendSerializer, UserLoginSerializer,
    UserFollowsSerializer, EmailToResetPasswordSerializer,
    RestorePasswordSerializer, AuthTokenMailSerializer, DeviceSerializer,
    UserOwnerVetSerializer
)
from .tasks import refer_a_friend_by_email, password_reset, send_feedback
from TapVet.utils import get_user_devices


class UserAuth(ObtainAuthToken):
    """
    Service to authenticate users.

    :accepted methods:
        POST
    """
    serializer_class = AuthTokenMailSerializer
    allowed_methods = ('POST',)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response(
                messages.bad_login,
                status=status.HTTP_400_BAD_REQUEST
            )
        user = serializer.validated_data['user']
        token = Token.objects.filter(user=user).first()
        if not token:
            return Response(
                messages.inactive,
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = UserLoginSerializer(user, context={'request': request})
        data = serializer.data
        if user.is_vet():
            data['is_verified'] = True if hasattr(
                user,
                'veterinarian'
            ) and user.veterinarian.verified else False
            data['is_locked'] = True if hasattr(
                user,
                'veterinarian'
            ) and user.veterinarian.locked else False
        return Response(data, status=status.HTTP_200_OK)


class UserView(ListCreateAPIView):
    """
    Service to create new users.
    Need authentication to list user

    :accepted methods:
    GET
    POST
    """
    serializer_class = CreateUserSerializer
    permission_classes = (permissions.AllowAny,)
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
        if request.user.is_authenticated():
            return self.list(request, *args, **kwargs)
        elif 'username' in request.GET or 'email' in request.GET:
            dic = {
                key: value
                for key, value in request.GET.iteritems()
                if key in ['username', 'email']
            }
            users = User.objects.filter(**dic)
            serializer = UserSerializers(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            message = {
                'detail': messages.user_login
            }
            return Response(
                message,
                status=status.HTTP_403_FORBIDDEN,
            )


class GroupsListView(ListAPIView):
    """
    Service to list users groups.

    :accepted methods:
    **GET
    """
    serializer_class = GroupsSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Group.objects.exclude(name__icontains='admin')
    allowed_methods = ('GET',)


class BreederListCreateView(ListCreateAPIView):
    """
    Service to create and list Breeder users. Need and authenticated user

    :accepted methods:
    **POST
    **GET
    """
    serializer_class = BreederSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Breeder.objects.all()

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


class VeterinarianListCreateView(ListCreateAPIView):
    """
    Service to create and list Veterinarians users. Need and authenticated user

    :accepted methods:
    **POST
    **GET
    """
    serializer_class = VeterinarianSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Veterinarian.objects.all()

    def create(self, request, *args, **kwargs):
        request.data['veterinarian_type'] = request.user.groups.id
        serializer = self.serializer_class(
            data=request.data,
            context={'user': request.user}
        )
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except (IntegrityError, ValueError, ValidationError) as e:
            error = {'detail': str(e)}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class AreaInterestListView(ListAPIView):
    '''
    List for Area of Interest.
    Required:
    **User Authenticated
    Allowed Methods:
    **GET = Only to list.
    '''
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AreaInterestSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = AreaInterest.objects.all()
        if user.is_vet_student():
            queryset = self.filter_student_areas(queryset)
        return queryset

    @staticmethod
    def filter_student_areas(areas_interest):
        student_areas = ['Small Animal', 'Large Animal', 'Other']
        return [area for area in areas_interest if area.name in student_areas]


class UserRetrieveUpdateView(RetrieveUpdateDestroyAPIView):
    '''
    One view to rule them all, one view to edit them.

    Retrive and Update:
    1) Users
    2) Pets Owners
    3) Breeders
    4) Veterinarians
    5) Students
    6) Technicians

    Accepted Methods:

    GET = Retrive the object
    PUT = Modify the entire object, need the full instace
    PATCH = Modify only the needed fields
    '''
    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = UserUpdateSerializer
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_authenticated:
            if not request.user.is_vet() and instance.is_vet():
                self.serializer_class = UserOwnerVetSerializer
        else:
            veterinarian = bool(self.request.query_params.get('vet', None))
            pet_owner = bool(self.request.query_params.get('owner', None))
            if xor(veterinarian, pet_owner):
                if not veterinarian and instance.is_vet():
                    self.serializer_class = UserOwnerVetSerializer
            else:
                return Response(
                    'Invalid query params',
                    status=status.HTTP_400_BAD_REQUEST
                )
        serializer = self.get_serializer(instance)
        return Response(
            self.get_verified_and_locked_out(serializer.data)
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.serializer_class(
            instance,
            data=request.data,
            partial=partial,
            context={
                'user': request.user,
                'request': request,
            }
        )
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_update(serializer)
        except ValueError as e:
            error = {'detail': str(e)}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

    def get_queryset(self):
        params = {
            'follows_count': Count('follows', distinct=True),
            'followed_by_count': Count('followed_by', distinct=True),
            'comments_count': Count('comments', distinct=True),
            'interest_count': Count('posts__likers', distinct=True),
            'upvotes_count': Count('comments__upvoters', distinct=True)
        }

        if self.request.user.is_authenticated():
            params = dict(
                params,
                followed=Case(
                    When(
                        pk__in=self.request.user.follows.all(),
                        then=Value(True)
                    ),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )
        qs = self.queryset.annotate(**params).select_related('groups')
        return qs.all()

    def delete(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {
                    'detail': messages.admin_delete
                },
                status.HTTP_401_UNAUTHORIZED)
        return self.destroy(request, *args, **kwargs)

    @staticmethod
    def get_verified_and_locked_out(data):
        veterinarian_data = data.get('veterinarian', None)
        if veterinarian_data:
            data['is_verified'] = veterinarian_data.pop('verified')
            data['is_locked'] = veterinarian_data.pop('locked')
        return data


class UserFollowView(APIView):
    """
    Service to follow and unfollow a user.
    :Auth Required:
    :accepted methods:
    POST
    DELETE
    """
    allowed_methods = ('POST', 'DELETE')
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, **kwargs):
        user = self.get_user(kwargs['pk'])
        add_user = False
        if request.user.is_vet():
            if user.is_vet():
                is_verified = hasattr(
                    request.user,
                    'veterinarian'
                ) and request.user.veterinarian.verified
                if is_verified:
                    add_user = True
                else:
                    return Response(
                        messages.follow_forbidden_not_verified,
                        status=status.HTTP_403_FORBIDDEN
                    )
        elif not user.is_vet():
            add_user = True
        if add_user:
            if user.id == request.user.id:
                return Response(
                    messages.follow_yourself_forbidden,
                    status=status.HTTP_403_FORBIDDEN
                )
            request.user.follows.add(user.id)
            return Response(status=status.HTTP_201_CREATED)
        return Response(
            messages.follow_permission,
            status=status.HTTP_403_FORBIDDEN
        )

    @staticmethod
    def delete(request, **kwargs):
        user = get_object_or_404(User, pk=kwargs['pk'])
        request.user.follows.remove(user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def get_user(user_id):
        user = User.objects.filter(pk=user_id).select_related('groups').first()
        if user:
            return user
        raise Http404()


class UserFeedBackView(APIView):
    """
    Service to send user feedback to admin.
    :Auth Required:
    :accepted methods:
    POST = The message will be receive on 'message'
    """
    allowed_methods = ('POST',)
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request, **kwargs):
        message_body = request.data.get('message', None)
        send_feedback(request.user, message_body)

        return Response(status=status.HTTP_204_NO_CONTENT)


class ReferFriendView(GenericAPIView):
    """
    Refer a friend endpoint
    :accepted methods:
        POST
    """
    serializer_class = ReferFriendSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        refer_a_friend_by_email(
            serializer.validated_data['email'],
            request.user
        )
        return Response(messages.request_successfully)


class UserFollowsListView(ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserFollowsSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk', None))
        qs = user.follows.select_related('image', 'groups')
        request_user = self.request.user
        if request_user.is_authenticated():
            qs = qs.annotate(
                following=Case(
                    When(
                        pk__in=request_user.follows.all(),
                        then=Value(True)
                    ),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )
        return [
            obj
            for obj in qs
            if hasattr(obj, 'veterinarian') and obj.veterinarian.verified
        ] if user.is_vet() else qs


class UserFollowedListView(UserFollowsListView):
    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk', None))
        qs = user.followed_by.select_related('image', 'groups')
        request_user = self.request.user
        if request_user.is_authenticated():
            qs = qs.annotate(
                following=Case(
                    When(
                        pk__in=request_user.follows.all(),
                        then=Value(True)
                    ),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )
        return qs


class EmailToResetPasswordView(GenericAPIView):
    serializer_class = EmailToResetPasswordSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['email']
        verification_code, created = VerificationCode.objects.get_or_create(
            user=user
        )
        if not created:
            if verification_code.has_expired():
                verification_code.delete()
                verification_code = VerificationCode(user=user)
                verification_code.save()
        password_reset(user, verification_code.code)
        return Response(messages.request_successfully)


class RestorePasswordView(GenericAPIView):
    serializer_class = RestorePasswordSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            verification_code = VerificationCode.objects.filter(
                code=serializer.validated_data['verification_code']
            ).select_related('user').first()
            if verification_code:
                has_expired = verification_code.has_expired()
                verification_code.delete()
                if has_expired:
                    return self.bad_request(messages.code_has_expired)
                user = verification_code.user
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response(messages.request_successfully)
            return self.bad_request(messages.invalid_code)
        error_message = serializer.errors.get('non_field_errors', None)
        error_data = {
            'detail': error_message[0]
        } if error_message else serializer.errors
        return self.bad_request(error_data)

    @staticmethod
    def bad_request(data):
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class DeviceView(GenericAPIView):
    serializer_class = DeviceSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        gcm_device, apns_device = get_user_devices(request.user.id)
        device = {
            "user": request.user,
            "registration_id": data['device_token']
        }

        if not gcm_device and not apns_device:
            try:
                if data['platform'] == serializer.IOS:
                    APNSDevice.objects.create(**device)
                else:
                    GCMDevice.objects.create(**device)
            except IntegrityError:
                pass
        elif gcm_device:
            try:
                if data['platform'] == serializer.IOS:
                    APNSDevice.objects.create(**device)
                    gcm_device.delete()
                else:
                    gcm_device.registration_id = data['device_token']
                    gcm_device.save()
            except IntegrityError:
                pass
        elif apns_device:
            try:
                if data['platform'] == serializer.ANDROID:
                    GCMDevice.objects.create(**device)
                    apns_device.delete()
                else:
                    apns_device.registration_id = data['device_token']
                    apns_device.save()
            except IntegrityError:
                pass

        return Response(
            messages.request_successfully,
            status=status.HTTP_201_CREATED
        )

    @staticmethod
    def delete(request, **kwargs):
        gcm_device, apns_device = get_user_devices(request.user.id)
        if gcm_device:
            gcm_device.delete()
        if apns_device:
            apns_device.delete()
        return Response(
            messages.request_successfully,
            status=status.HTTP_204_NO_CONTENT
        )


class UserDeactive(GenericAPIView):
    '''
    Service to manage the user sessions.
    METHODS
    DELETE
    * Delete the auth token for the self user.
    '''

    permission_classes = (permissions.IsAuthenticated,)
    allowed_methods = ('DELETE', )

    @staticmethod
    def delete(request, **kwargs):
        user = request.user
        if not (user.is_superuser or user.is_staff):
            user.is_active = False
            user.save()
            Token.objects.filter(user=user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
