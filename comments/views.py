from django.db.models import Count
from django.shortcuts import get_object_or_404

from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from TapVet.pagination import StandardPagination
from TapVet import messages
from posts.models import Post

from .models import Comment
from .permissions import IsPetOwner
from .serializers import CommentSerializer


class CommentsPetOwnerListCreateView(ListCreateAPIView):
    """
    Service to create and list Pet Owner comments for post.
    :Auth Required:
    :accepted methods:
    GET
    POST
    """
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated, IsPetOwner)
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = Comment.objects.filter(
            post_id=self.kwargs['pk'], user__groups_id__in=[1, 2]
        ).annotate(
            upvoters_count=Count('upvoters')).order_by('-upvoters_count')
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        post = get_object_or_404(Post, pk=kwargs['pk'])
        if not post.is_paid():
            if post.user.is_vet():
                if not request.user.has_perm('users.is_vet'):
                    return Response(
                        messages.comment_permission,
                        status=status.HTTP_403_FORBIDDEN)
            else:
                if not request.user.has_perm('users.is_pet_owner'):
                    return Response(
                        messages.comment_permission,
                        status=status.HTTP_403_FORBIDDEN)
        serializer.save(post=post)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CommentsVetListCreateView(CommentsPetOwnerListCreateView):
    """
    Service to create and list Vet comments for post.
    :Auth Required:
    :accepted methods:
    GET
    POST
    """
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        qs = Comment.objects.filter(
            post_id=self.kwargs['pk'], user__groups_id__in=[3, 4, 5]
        ).annotate(
            upvoters_count=Count('upvoters')).order_by('-upvoters_count')
        return qs


class CommentVoteView(APIView):
    """
    Service to upvote and downvote a comment.
    :Auth Required:
    :accepted methods:
    POST
    DELETE
    """
    allowed_methods = ('POST', 'DELETE')
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs['pk'])
        comment.upvoters.add(request.user.id)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs['pk'])
        comment.upvoters.remove(request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)
