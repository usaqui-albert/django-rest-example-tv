from django.db.models import Count
from django.http import Http404

from rest_framework.generics import ListAPIView, DestroyAPIView
from rest_framework import permissions
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from TapVet.pagination import StandardPagination

from ..serializers import CommentSerializer, CommentVetSerializer
from ..models import Comment, Feedback

from .serializers import AdminFeedbackSerializer


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
    serializer_class = AdminFeedbackSerializer
    pagination_class = StandardPagination
    permission_classes = (permissions.IsAdminUser,)
    filter_backends = (SearchFilter, )
    search_fields = (
        'user__full_name', 'comment__user__full_name',
        'user__email', 'comment__user__email',
        'user__username', 'comment__user__username',
    )
    queryset = Feedback.objects.select_related(
        'user',
        'comment__user__veterinarian',
        'user__image'
    ).order_by('-id')
