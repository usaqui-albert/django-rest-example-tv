import stripe
from stripe.error import CardError, InvalidRequestError, APIConnectionError

from django.conf import settings
from django.db import IntegrityError
from django.db.models import Count, Value, Case, When, BooleanField
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
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

from .models import User, Breeder, Veterinarian, AreaInterest
from helpers.stripe_helpers import (
    stripe_errors_handler, get_customer_in_stripe, card_list,
    get_first_card_token, add_card_to_customer, delete_card_from_customer
)
from .serializers import (
    CreateUserSerializer, UserSerializers, VeterinarianSerializer,
    BreederSerializer, GroupsSerializer, AreaInterestSerializer,
    UserUpdateSerializer, ReferFriendSerializer, UserLoginSerializer,
    UserFollowsSerializer
)
from .tasks import send_mail, refer_a_friend_by_email


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
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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
    queryset = AreaInterest.objects.all()


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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.serializer_class(
            instance,
            data=request.data,
            partial=partial,
            context={'user': request.user}
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
        qs = self.queryset.annotate(**params)
        return qs.all()

    def delete(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {
                    'detail': messages.admin_delete
                },
                status.HTTP_401_UNAUTHORIZED)
        return self.destroy(request, *args, **kwargs)


class StripeCustomerView(APIView):
    """Service to create a stripe customer for a TapVet user

    :accepted methods:
        POST
        GET
    """

    def __init__(self, **kwargs):
        super(StripeCustomerView, self).__init__(**kwargs)
        stripe.api_key = settings.STRIPE_API_KEY

    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request, **kwargs):
        """

        :param request:
        :param kwargs:
        :return:
        """
        user = request.user
        if user.id == int(kwargs['pk']):
            token = request.data.get('token', None)
            if token:
                if user.stripe_token:
                    customer = get_customer_in_stripe(user)
                    if isinstance(customer, str):
                        response_msg = customer
                    else:
                        card_token = get_first_card_token(
                            customer.sources.data)
                        added = add_card_to_customer(customer, token)
                        if added is True:
                            deleted = delete_card_from_customer(
                                customer,
                                card_token
                            )
                            if deleted is True:
                                return Response(
                                    {'stripe': user.stripe_token},
                                    status=status.HTTP_200_OK
                                )
                            else:
                                response_msg = deleted
                        else:
                            response_msg = added
                else:
                    try:
                        customer = stripe.Customer.create(
                            source=token,
                            description='Customer for %s' % user.__str__()
                        )
                    except (
                        APIConnectionError, InvalidRequestError,
                        CardError
                    ) as err:
                        response_msg = {
                            'detail': stripe_errors_handler(err)}
                    else:
                        cus_token = customer.id
                        user.stripe_token = cus_token
                        user.save()
                        return Response(
                            {'stripe': cus_token},
                            status=status.HTTP_201_CREATED
                        )
            else:
                response_msg = {'detail': 'Token field is required'}
            return Response(response_msg, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            messages.forbidden_action,
            status=status.HTTP_403_FORBIDDEN
        )

    @staticmethod
    def get(request, **kwargs):
        """

        :param request:
        :param kwargs:
        :return:
        """
        user = request.user
        if user.id == int(kwargs['pk']):
            customer = get_customer_in_stripe(user)
            if isinstance(customer, str):
                return Response(
                    {"detail": customer},
                    status=status.HTTP_404_NOT_FOUND
                )
            cards = customer.sources.data
            return Response(card_list(cards))
        return Response(
            messages.forbidden_action,
            status=status.HTTP_403_FORBIDDEN
        )


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
        message_title = "[TapVet] New Feedback"
        message_body = request.data.get('message', None)
        msg_html = render_to_string(
            'users/partials/email/feedback.html',
            {
                'user': request.user,
                'message': message_body
            }
        )
        send_mail.delay(
            message_title, message_body, msg_html, True)

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
        refer_a_friend_by_email.delay(
            serializer.validated_data['email'],
            request.user.full_name
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
