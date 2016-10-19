import stripe
from stripe.error import CardError, InvalidRequestError, APIConnectionError

from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group

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
from helpers.stripe_helpers import stripe_errors_handler
from .serializers import (
    CreateUserSerializer, UserSerializers, VeterinarianSerializer,
    BreederSerializer, GroupsSerializer, AreaInterestSerializer,
    UserUpdateSerializer
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
            msg = {'detail': messages.bad_login}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                'token': token.key,
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'groups' : user.groups.id
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
                "detail": messages.user_login
            }
            return Response(
                message,
                status=status.HTTP_403_FORBIDDEN,
            )
        return self.list(request, *args, **kwargs)


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
    queryset = Group.objects.all()
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
    queryset = User.objects.all()

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
                        response_msg = {'detail': 'You already have a customer in stripe'}
                    else:
                        try:
                            customer = stripe.Customer.create(
                                source=token,
                                description='Customer for %s' % user.__str__()
                            )
                        except (APIConnectionError, InvalidRequestError, CardError) as err:
                            response_msg = {'detail': stripe_errors_handler(err)}
                        else:
                            cus_token = customer.id
                            user.stripe_token = cus_token
                            user.save()
                            return Response('Customer successfully created')
                else:
                    response_msg = {'detail': 'Token field can not be empty'}
            else:
                response_msg = {'detail': 'Token field is required'}
            return Response(response_msg, status=status.HTTP_400_BAD_REQUEST)
        response_msg = {'detail': 'You are not allow to do this action'}
        return Response(response_msg, status=status.HTTP_403_FORBIDDEN)
