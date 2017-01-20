from django.db.models import Q

from rest_framework.generics import ListAPIView

from .models import Activity
from .serializers import ActivitySerializer


class UserLikedPostListView(ListAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

    def get_queryset(self):
        qs = self.queryset
        qs = qs.filter(user=self.request.user, action=Activity.LIKE)
        return qs.all()


class UserCommentPostListView(ListAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

    def get_queryset(self):
        qs = self.queryset
        qs = qs.filter(user=self.request.user, action=Activity.COMMENT)
        return qs.all()


class ActivityListView(ListAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

    def get_queryset(self):
        user = self.request.user
        qs = self.queryset
        qs = qs.filter(
            Q(
                post__user=user, action=Activity.LIKE
            ) |
            Q(
                comment__user=user, action=Activity.UPVOTE  #c
            ) |
            Q(
                post__user=user, action=Activity.COMMENT  #a
            )
        )
        return qs.all()
