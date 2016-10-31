from django.db.models import Count
from rest_framework.generics import ListCreateAPIView

from posts.models import Post

from .models import Comment


class CommentsListCreateView(ListCreateAPIView):
    """
    Service to create list and create new comments for post.

    :accepted methods:
    GET
    POST
    """
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def get_queryset(self):
        qs = Comment.objects.filter(
            post_id=self.kwargs['pk']
        ).annotate(upvoters_count=Count('upvoters'))
        return qs
