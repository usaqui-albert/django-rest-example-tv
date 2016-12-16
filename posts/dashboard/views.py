from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.filters import SearchFilter, DjangoFilterBackend

from TapVet.pagination import StandardPagination
from ..models import Post
from .serializers import AdminPostSerializer


class AdminPostView(ListAPIView):
    serializer_class = AdminPostSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = StandardPagination
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('user__username', 'user__full_name', 'user__email',
                     'description')
    filter_fields = ('reports__type',)
    queryset = Post.objects.all().select_related(
        'user__groups',
        'user__image',
    ).prefetch_related(
        'images'
    ).order_by('-id').distinct()
