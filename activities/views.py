from itertools import chain

from django.db.models import Value, CharField

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
        qs = qs.filter(
            user=user, action=Activity.LIKE, active=True).select_related(
            'user__groups',
            'user__image',
            'post__pet',
            'post__user__groups',
            'post__user__image',
            'comment__user__groups',
            'comment__user__image',
        ).prefetch_related(
            'post__images',
        )

        return qs.all().order_by('-updated_at')


class UserCommentPostListView(ListAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        qs = qs.filter(
            user=user, action=Activity.COMMENT, active=True).select_related(
            'user__groups',
            'user__image',
            'post__pet',
            'post__user__groups',
            'post__user__image',
            'comment__user__groups',
            'comment__user__image',
        ).prefetch_related(
            'post__images',
        )

        return qs.all().order_by('-updated_at')


class ActivityListView(ListAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardPagination

    def get_queryset(self):
        user = self.request.user

        qs1 = self.helper(
            Activity.objects.filter(
                post__user=user,
                action=Activity.LIKE
            ).annotate(
                beacon=Value(
                    'Like',
                    output_field=CharField()
                )
            ),
            user
        )

        qs2 = self.helper(
            Activity.objects.filter(
                comment__user=user,
                action=Activity.UPVOTE
            ).annotate(
                beacon=Value(
                    'Upvote',
                    output_field=CharField()
                )
            ),
            user
        )

        qs3 = self.helper(
            Activity.objects.filter(
                post__user=user,
                action=Activity.COMMENT
            ).annotate(
                beacon=Value(
                    'Comment', output_field=CharField()
                )
            ),
            user
        )

        qs4 = self.helper(
            Activity.objects.filter(
                post__in=user.likes.all(),
                action=Activity.COMMENT
            ).annotate(
                beacon=Value(
                    'Like_Comment',
                    output_field=CharField()
                )
            ),
            user
        )

        return sorted(
            chain(qs1, qs2, qs3, qs4),
            key=lambda instance: instance.updated_at,
            reverse=True
        )

    @staticmethod
    def helper(qs, user):
        select_tuples = (
            'user__groups',
            'user__image',
            'post__pet',
            'post__user__groups',
            'post__user__image',
            'comment__user__groups',
            'comment__user__image',
        )
        return qs.exclude(user=user).select_related(
            *select_tuples
        ).prefetch_related(
            'post__images',
        )
