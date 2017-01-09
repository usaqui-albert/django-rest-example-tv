from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.filters import SearchFilter, DjangoFilterBackend

from TapVet.pagination import StandardPagination
from ..models import Post
from .serializers import AdminPostSerializer, AdminPostActiveDeactiveSerializer


class AdminPostView(ListAPIView):
    '''
    Admin Post View
    Search Fields = "username", "full_name", "email", "description"
    Filter Fields = "reports_type", "active"
    Method Allowed:
    GET
    '''
    serializer_class = AdminPostSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = StandardPagination
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('user__username', 'user__full_name', 'user__email',
                     'description')
    filter_fields = ('reports__type', 'active')
    queryset = Post.objects.all().select_related(
        'user__groups',
        'user__image',
    ).prefetch_related(
        'images'
    ).order_by('-id').distinct()


class AdminActiveDeactivePostView(UpdateAPIView):
    '''
        View to active and deactive a post
        Method Allowed:
        PATCH
    '''
    serializer_class = AdminPostActiveDeactiveSerializer
    permission_classes = (IsAdminUser,)
    allowed_methods = ('PATCH',)
    queryset = Post.objects.all()
