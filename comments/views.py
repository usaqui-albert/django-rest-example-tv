from django.db.models import Count
from django.http import Http404
from django.utils import timezone

from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response

from TapVet.pagination import StandardPagination
from TapVet.permissions import IsPetOwner
from TapVet import messages
from posts.models import Post

from .models import Comment
from .serializers import CommentSerializer

from django.db.models import Case, Value, When, BooleanField


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
            upvoters_count=Count('upvoters'),
            voted=Case(
                When(pk__in=self.request.user.upvotes.all(), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        ).select_related('user__groups').order_by('-upvoters_count')
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        post = self.get_post(kwargs['pk'])
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

    def get_post(self, pk):
        qs = Post.objects.filter(
            pk=pk
        ).select_related('user__groups')
        if not qs:
            raise Http404()
        aux = list(qs)
        qs.update(updated_at=timezone.now())
        return aux[0]


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
            upvoters_count=Count('upvoters')
        ).select_related('user__groups').order_by('-upvoters_count')
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

    def update_post(self, pk):
        qs = Post.objects.filter(pk=pk)
        qs.update(updated_at=timezone.now())

    def post(self, request, *args, **kwargs):
        comment = Comment.objects.filter(
            pk=kwargs['pk']).select_related('post').first()
        self.update_post(pk=comment.post.id)
        comment.upvoters.add(request.user.id)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        comment = Comment.objects.filter(
            pk=kwargs['pk']).select_related('post').first()
        self.update_post(pk=comment.post.id)
        comment.upvoters.remove(request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)
