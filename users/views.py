import stripe
from stripe.error import CardError, InvalidRequestError, APIConnectionError

from django.db import IntegrityError
from django.db.models import Count, Value, Case, When, BooleanField
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from django.template.loader import render_to_string


from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework import status

from TapVet import messages
from TapVet.settings import STRIPE_API_KEY

from .permissions import IsOwnerOrReadOnly
from .models import User, Breeder, Veterinarian, AreaInterest
from helpers.stripe_helpers import (
    stripe_errors_handler, get_customer_in_stripe, card_list
)
from .serializers import (
    CreateUserSerializer, UserSerializers, VeterinarianSerializer,
    BreederSerializer, GroupsSerializer, AreaInterestSerializer,
    UserUpdateSerializer, ReferFriendSerializer, UserLoginSerializer
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
                messages.bad_login, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.validated_data['user']
        token = Token.objects.filter(user=user).first()
        if not token:
            return Response(
                messages.inactive, status=status.HTTP_403_FORBIDDEN)
        serializer = UserLoginSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
                "detail": messages.user_login
            }
            return Response(
                message,
                status=status.HTTP_403_FORBIDDEN,
            )


class UserGetUpdateView(generics.RetrieveUpdateDestroyAPIView):
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
    allowed_methods = ('GET', 'PUT', 'PATCH', 'DELETE')
    queryset = User.objects.all()

    def delete(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {
                    'detail': messages.admin_delete
                },
                status.HTTP_401_UNAUTHORIZED)
        return self.destroy(request, *args, **kwargs)


class GroupsListView(generics.ListAPIView):
    """
    Service to list users groups.

    :accepted methods:
    **GET
    """
    serializer_class = GroupsSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Group.objects.exclude(name__icontains='admin')
    allowed_methods = ('GET',)


class BreederListCreateView(generics.ListCreateAPIView):
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


class VeterinarianListCreateView(generics.ListCreateAPIView):
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


class AuthorizeBreederView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    serializer_class = BreederSerializer
    allowed_methods = ('PATCH',)

    def patch(self, request, *args, **kwargs):
        breeder = get_object_or_404(Breeder, id=kwargs['pk'])
        breeder.verified = request.POST.get('verified', False)
        breeder.save()
        serializer = self.serializer_class(breeder)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class AuthorizeVetView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    serializer_class = VeterinarianSerializer
    allowed_methods = ('PATCH',)

    def patch(self, request, *args, **kwargs):
        vet = get_object_or_404(Veterinarian, id=kwargs['pk'])
        vet.verified = request.POST.get('verified', False)
        vet.save()
        serializer = self.serializer_class(vet)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class AreaInterestListView(generics.ListAPIView):
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


class UserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
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
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
    serializer_class = UserUpdateSerializer
    queryset = User.objects.annotate(
        follows_count=Count('follows', distinct=True),
        followed_by_count=Count('followed_by', distinct=True),
        comments_count=Count('comments', distinct=True),
        interest_count=Count('posts__likers', distinct=True),
        upvotes_count=Count('comments__upvoters', distinct=True)
    )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_update(serializer)
        except ValueError as e:
            error = {'detail': str(e)}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

    def get_queryset(self):
        qs = self.queryset
        if self.request.user.is_authenticated():
            qs = qs.annotate(
                followed=Case(
                    When(
                        pk__in=self.request.user.follows.all(),
                        then=Value(True)
                    ),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )
        return qs.all()


class StripeCustomerView(APIView):
    """Service to create a stripe customer for a TapVet user

    :accepted methods:
        POST
        GET
    """

    def __init__(self, **kwargs):
        super(StripeCustomerView, self).__init__(**kwargs)
        stripe.api_key = STRIPE_API_KEY

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
            if 'token' in request.data:
                token = request.data.get('token')
                if token:
                    if user.stripe_token:
                        response_msg = {
                            'detail': 'You already have a customer in stripe'}
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
                            return Response({'stripe': cus_token})
                else:
                    response_msg = {'detail': 'Token field can not be empty'}
            else:
                response_msg = {'detail': 'Token field is required'}
            return Response(response_msg, status=status.HTTP_400_BAD_REQUEST)
        response_msg = {'detail': 'You are not allowed to do this action'}
        return Response(response_msg, status=status.HTTP_403_FORBIDDEN)

    @staticmethod
    def get(request, **kwargs):
        """

        :param request:
        :param kwargs:
        :return:
        """
        user = request.user
        if user.id == int(kwargs['pk']):
            if user.stripe_token:
                customer = get_customer_in_stripe(user)
                cards = customer.sources.data
                return Response(card_list(cards))
            no_customer_response = {
                'detail': 'There is no customer for this user'}
            return Response(
                no_customer_response, status=status.HTTP_404_NOT_FOUND)
        response_msg = {'detail': 'You are not allowed to do this action'}
        return Response(response_msg, status=status.HTTP_403_FORBIDDEN)


class UserFollowView(APIView):
    """
    Service to follow and unfollow a user.
    :Auth Required:
    :accepted methods:
    POST
    DELETE
    """
    allowed_methods = ('POST', 'DELETE')
    permission_classes = (permissions.IsAuthenticated, )

    def forbidden(self):
        return Response(
            messages.follow_permission,
            status=status.HTTP_403_FORBIDDEN
        )

    def post(self, request, **kwargs):
        user = get_object_or_404(User, pk=kwargs['pk'])
        if request.user.has_perm('users.is_vet'):
            if not user.is_vet():
                return self.forbidden()
            else:
                try:
                    if not user.veterinarian.verified:
                        return self.forbidden()
                except:
                    return self.forbidden()
        else:
            if user.is_vet():
                return self.forbidden()
        user.follows.add(request.user.id)
        return Response(status=status.HTTP_201_CREATED)

    @staticmethod
    def delete(request, **kwargs):
        user = get_object_or_404(User, pk=kwargs['pk'])
        user.follows.remove(request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserFeedBackView(APIView):
    """
    Service to send user feedback to admin.
    :Auth Required:
    :accepted methods:
    POST = The message will be receive on 'message'
    """
    allowed_methods = ('POST', )
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
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


class ReferFriendView(generics.GenericAPIView):
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
