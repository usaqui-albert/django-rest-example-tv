from rest_framework.generics import (
    ListAPIView, RetrieveUpdateAPIView
)
from rest_framework.permissions import IsAdminUser
from rest_framework.filters import (
    SearchFilter, DjangoFilterBackend, OrderingFilter
)

from TapVet.pagination import StandardPagination
from ..models import Post
from .serializers import AdminPostSerializer


class AdminPostView(ListAPIView):
    '''
    Admin Post View
    Search Fields = "username", "full_name", "email", "description"
    Filter Fields = "reports_type", "active"
    Ordering Fields = "created_at"
    Method Allowed:
    GET
    '''
    serializer_class = AdminPostSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = StandardPagination
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ('user__username', 'user__full_name', 'user__email',
                     'description')
    filter_fields = ('reports__type', 'active')
    ordering_fields = ('created_at',)
    queryset = Post.objects.all().select_related(
        'user__groups',
        'user__image',
    ).prefetch_related(
        'images'
    ).order_by('-id').distinct()


class AdminPostDetailView(RetrieveUpdateAPIView):
    '''
        View to get the full detail of a post or active or deactive it.
        Method Allowed:
        PATCH
        GET
    '''
    serializer_class = AdminPostSerializer
    permission_classes = (IsAdminUser,)
    allowed_methods = ('PATCH', 'GET')
    queryset = Post.objects.all().select_related('user__image')
