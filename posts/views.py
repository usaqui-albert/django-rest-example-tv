from django.shortcuts import render

from rest_framework.generics import ListCreateAPIView

class PostVetListCreateView(ListCreateAPIView):
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
