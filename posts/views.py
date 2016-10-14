from django.db.models import Count

from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView
from rest_framework import permissions, status

from .serializers import PostPetOwnerSerializer
from .models import Post


class PostPetOwnerListCreateView(ListCreateAPIView):
    """
    Service to create list and create new vet post.

    :accepted methods:
    GET
    POST
    """
    serializer_class = PostPetOwnerSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Post.objects.annotate(likes_count=Count('likers'))

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)
