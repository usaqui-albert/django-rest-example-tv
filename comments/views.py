from django.db.models import Count
from django.http import Http404
from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework.generics import ListCreateAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response

from TapVet.pagination import StandardPagination
from TapVet.permissions import IsPetOwner
from TapVet import messages
from posts.models import Post

from .models import Comment, Feedback
from .serializers import (
    CommentSerializer, CommentVetSerializer, FeedbackSerializer)

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
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = StandardPagination
    groups_ids = [1, 2]

    def get_queryset(self):
        annotate_params = {'upvoters_count': Count('upvoters')}
        if self.request.user.is_authenticated():
            annotate_params['upvoted'] = Case(
                When(
                    pk__in=self.request.user.upvotes.all(),
                    then=Value(True)
                ),
                default=Value(False),
                output_field=BooleanField(),
            )
        qs = Comment.objects.filter(
            post_id=self.kwargs['pk'],
            user__groups_id__in=self.groups_ids
        ).annotate(
            **annotate_params
        ).select_related(
            'user__groups'
        ).order_by('-upvoters_count', '-updated_at')
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
            dict(serializer.data, upvoters_count=0),
            status=status.HTTP_201_CREATED, headers=headers)

    @staticmethod
    def get_post(pk):
        qs = Post.objects.filter(pk=pk).select_related('user__groups').first()
        if qs:
            qs.save()
            return qs
        raise Http404()


class CommentsVetListCreateView(CommentsPetOwnerListCreateView):
    """
    Service to create and list Vet comments for post.
    :Auth Required:
    :accepted methods:
    GET
    POST
    """
    serializer_class = CommentVetSerializer
    groups_ids = [3, 4, 5]


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


class FeedbackCreateView(CreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Feedback

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={
                'user': request.user,
                'comment': get_object_or_404(
                    Comment, pk=kwargs.get('pk', None)
                )
            }
        )
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except ValueError as e:
            return Response(
                messages.feedback_user, status=status.HTTP_400_BAD_REQUEST
            )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)
