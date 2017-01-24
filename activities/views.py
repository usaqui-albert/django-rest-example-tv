from django.db.models import Q

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from TapVet.pagination import StandardPagination

from .models import Activity
from .serializers import ActivitySerializer


class UserLikedPostListView(ListAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        qs = qs.filter(user=user, action=Activity.LIKE).select_related(
            'user',
            'user__groups',
            'user__image',
            'post',
            'post__user',
            'post__pet',
            'post__user__groups',
            'post__user__image',
            'comment',
            'comment__user',
            'comment__user__groups',
            'comment__user__image',
        ).prefetch_related(
            'post__images',
        )

        return qs.all()


class UserCommentPostListView(ListAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        qs = qs.filter(user=user, action=Activity.COMMENT).select_related(
            'user',
            'user__groups',
            'user__image',
            'post',
            'post__user',
            'post__pet',
            'post__user__groups',
            'post__user__image',
            'comment',
            'comment__user',
            'comment__user__groups',
            'comment__user__image',
        ).prefetch_related(
            'post__images',
        )

        return qs.all()


class ActivityListView(ListAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardPagination

    def get_queryset(self):
        user = self.request.user
        qs = self.queryset
        qs = qs.filter(
            Q(
                post__user=user, action=Activity.LIKE
            ) |
            Q(
                comment__user=user, action=Activity.UPVOTE
            ) |
            Q(
                post__user=user, action=Activity.COMMENT
            ) |
            Q(
                post__in=user.likes.all(), action=Activity.COMMENT
            )
        ).exclude(user=user).select_related(
            'user',
            'user__groups',
            'user__image',
            'post',
            'post__user',
            'post__pet',
            'post__user__groups',
            'post__user__image',
            'comment',
            'comment__user',
            'comment__user__groups',
            'comment__user__image',
        ).prefetch_related(
            'post__images',
        )
        return qs.all()
