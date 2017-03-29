from rest_framework.generics import (
    ListAPIView, RetrieveUpdateAPIView
)
from rest_framework.permissions import IsAdminUser
from rest_framework.filters import (
    SearchFilter, DjangoFilterBackend, OrderingFilter
)
from rest_framework.serializers import BooleanField

from TapVet.pagination import StandardPagination
from activities.models import Activity

from ..models import Post
from .serializers import AdminPostSerializer


class AdminPostView(ListAPIView):
    '''
    Admin Post View
    Search Fields = "username", "full_name", "email", "description"
    Ordering Fields = "created_at"
    Filter Fields = "reports_type", "active", "visible_by_vet",
    "visible_by_owner"
    Method Allowed:
    GET
    '''
    serializer_class = AdminPostSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = StandardPagination
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    filter_fields = ('reports__type', 'active')
    ordering_fields = ('created_at',)
    search_fields = (
        'user__username', 'user__full_name', 'user__email', 'description'
    )
    filter_fields = (
        'reports__type', 'active', 'visible_by_vet', 'visible_by_owner'
    )
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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        active = None
        if 'active' in request.data:
            active = BooleanField().to_representation(request.data['active'])
        if (
            ('active' in request.data) and
            active != instance.active
        ):
            Activity.objects.filter(
                post=instance).update(active=active)
        return super(
            AdminPostDetailView, self
        ).update(request, *args, **kwargs)
