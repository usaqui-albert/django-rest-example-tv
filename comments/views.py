from django.db.models import Count
from rest_framework.generics import ListCreateAPIView
from rest_framework import permissions

from .models import Comment
from .serializers import CommentSerializer


class CommentsPetOwnerListCreateView(ListCreateAPIView):
    """
    Service to create and list Pet Owner comments for post.

    :accepted methods:
    GET
    POST
    """
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        qs = Comment.objects.filter(
            post_id=self.kwargs['pk'], user__groups_id__in=[1, 2]
        ).annotate(upvoters_count=Count('upvoters'))
        return qs


class CommentsVetListCreateView(ListCreateAPIView):
    """
    Service to create and list Vet comments for post.

    :accepted methods:
    GET
    POST
    """
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        qs = Comment.objects.filter(
            post_id=self.kwargs['pk'], user__groups_id__in=[3, 4, 5]
        ).annotate(upvoters_count=Count('upvoters'))
        return qs
