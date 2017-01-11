from django.db.models import Count

from rest_framework.generics import ListAPIView
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
