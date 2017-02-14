from django.db.models import Count
from django.http import Http404
from django.utils import timezone

from rest_framework.generics import ListCreateAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response

from TapVet.pagination import StandardPagination
from TapVet import messages
from posts.models import Post

from .models import Comment, Feedback
from .serializers import (
    CommentSerializer, CommentVetSerializer, FeedbackSerializer,
    CommentVetNamelessSerializer
)

from django.db.models import Case, Value, When, BooleanField
from django.db import IntegrityError


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
        user = self.request.user
        if user.is_authenticated():
            annotate_params['upvoted'] = Case(
                When(
                    pk__in=user.upvotes.all(),
                    then=Value(True)
                ),
                default=Value(False),
                output_field=BooleanField(),
            )
            post = self.get_post(self.kwargs['pk'])
            is_owner = int(post.user.id) == int(user.id)
            if post and is_owner:
                annotate_params['has_feedback'] = Case(
                    When(
                        pk__in=user.feedbacks.all(),
                        then=Value(True)
                    ),
                    default=Value(False),
                    output_field=BooleanField()
                )
        qs = Comment.objects.filter(
            post_id=self.kwargs['pk'],
            user__groups_id__in=self.groups_ids
        ).annotate(
            **annotate_params
        ).select_related(
            'user__groups'
        ).order_by('-updated_at', '-upvoters_count')
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
    serializer_class = CommentVetNamelessSerializer
    groups_ids = [3, 4, 5]

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.is_vet():
            self.serializer_class = CommentVetSerializer
        return self.list(request, *args, **kwargs)


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
        comment = self.get_comment(kwargs['pk'])
        if not request.user.id == comment.post.user_id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(
            data=request.data,
            context={
                'user': request.user,
                'comment': comment
            }
        )
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except (ValueError, IntegrityError) as e:
            if isinstance(e, IntegrityError):
                return Response(
                    messages.only_once_feedback,
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                messages.feedback_user, status=status.HTTP_400_BAD_REQUEST
            )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @staticmethod
    def get_comment(pk):
        comment = Comment.objects.filter(pk=pk).select_related(
            'post__user').first()
        if comment:
            return comment
        raise Http404()
