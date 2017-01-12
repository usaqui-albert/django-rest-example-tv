from django.db.models import Count
from django.http import Http404

from rest_framework.generics import ListAPIView, DestroyAPIView
from rest_framework import permissions

from ..serializers import CommentSerializer, CommentVetSerializer
from ..models import Comment
from TapVet.pagination import StandardPagination


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
