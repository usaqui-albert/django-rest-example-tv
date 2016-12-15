from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser

from TapVet.pagination import StandardPagination
from ..models import Post
from .serializers import AdminPostSerializer


class AdminPostView(ListAPIView):
    serializer_class = AdminPostSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = Post.objects.all().select_related(
            'user__groups',
            'user__image',
        ).prefetch_related(
            'images'
        ).order_by('-id')
        return queryset
