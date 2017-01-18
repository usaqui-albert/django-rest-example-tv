from django.db.models import Count
from django.http import Http404

from rest_framework.generics import (
    ListAPIView, DestroyAPIView, RetrieveAPIView
)
from rest_framework import permissions
from rest_framework.filters import OrderingFilter, SearchFilter

from django_filters.rest_framework import DjangoFilterBackend

from TapVet.pagination import StandardPagination

from ..serializers import CommentSerializer, CommentVetSerializer
from ..models import Comment, Feedback

from .serializers import AdminFeedbackListSerializer, AdminFeedbackSerializer


class PetOwnerCommentsView(ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAdminUser,)
    pagination_class = StandardPagination
    groups_ids = [1, 2]

    def get_queryset(self):
        qs = Comment.objects.filter(
            post_id=self.kwargs['pk'],
            user__groups_id__in=self.groups_ids
        ).annotate(
            upvoters_count=Count('upvoters')
        ).select_related(
            'user__groups'
        ).order_by('-upvoters_count', '-updated_at')
        return qs


class VetCommentsView(PetOwnerCommentsView):
    serializer_class = CommentVetSerializer
    groups_ids = [3, 4, 5]


class AdminCommentDetailView(DestroyAPIView):
    queryset = Comment.objects.all()
    permission_classes = (permissions.IsAdminUser,)

    def get_object(self):
        obj = self.queryset.filter(
            pk=self.kwargs['pk_comment'],
            post=self.kwargs['pk_post']
        ).first()
        if obj:
            return obj
        raise Http404()


class AdminFeedbackListView(ListAPIView):
    '''
    View for the admin dashboard. This view will paginate users by 20 per
    page.

    Will allow to change the amount of users per page by sending 'page_size'
    queryparam

    ORDERING FIELDS:
        * was_helpful

    SEARCH FIELDS:
        * user full_name
        * user email
        * user username
        * vet full_name
        * vet email
        * vet username

    EXAMPLES
    * ORDERING:
        -- api/v1/dashboard/feedback?ordering=was_helpful
        -- api/v1/dashboard/feedback?ordering=-was_helpful
        (Reverse of the above)
    * FILTERING:
       -- api/v1/dashboard/feedback?was_helpful=True
    * SEARCHING:
        -- api/v1/dashboard/feedback?search=<###>
    * PAGE SIZE:
        -- api/v1/dashboard/feedback?page_size=40

    '''
    serializer_class = AdminFeedbackListSerializer
    pagination_class = StandardPagination
    permission_classes = (permissions.IsAdminUser,)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = (
        'user__full_name', 'comment__user__full_name',
        'user__email', 'comment__user__email',
        'user__username', 'comment__user__username',
    )
    ordering_fields = ('was_helpful', )
    filter_fields = ('was_helpful', )
    queryset = Feedback.objects.select_related(
        'user',
        'comment__user__veterinarian',
        'user__image'
    ).order_by('-id')


class AdminFeedbackView(RetrieveAPIView):
    queryset = Feedback.objects.select_related(
        'user',
        'comment__user__veterinarian',
        'user__image',
        'comment__post'
    )
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = AdminFeedbackSerializer
