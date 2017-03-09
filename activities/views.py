from itertools import chain

from django.db.models import Value, CharField

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from TapVet.pagination import StandardPagination
from users.models import User
from posts.models import UserLikesPost

from .models import Activity
from .serializers import ActivitySerializer

select_tuples = (
    'user__groups',
    'user__image',
    'post__pet',
    'post__user__groups',
    'post__user__image',
    'comment__user__groups',
    'comment__user__image',
)


class UserLikedPostListView(ListAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardPagination

    def get_queryset(self):

        qs = self.queryset
        user = self.request.user
        qs = qs.filter(
            user=user, action=Activity.LIKE, active=True
        ).select_related(
            *select_tuples
        ).prefetch_related(
            'post__images',
        ).annotate(
            beacon=Value(
                'like',
                output_field=CharField()
            )
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
        # Verify is user is vet
        qs_params = {
            'comment__user': user,
            'action': Activity.COMMENT,
            'active': True
        }
        if user.is_vet():
            qs_params['post__user__groups__pk__in'] = User.IS_VET
        qs = qs.filter(
            **qs_params
        ).select_related(
            *select_tuples
        ).prefetch_related(
            'post__images',
        ).annotate(
            beacon=Value(
                'comment',
                output_field=CharField()
            )
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
                action=Activity.LIKE,
                active=True
            ).annotate(
                beacon=Value(
                    'like',
                    output_field=CharField()
                )
            ),
            user
        )
        # Verify user is vet
        qs2_params = {
            'comment__user': user,
            'action': Activity.UPVOTE,
            'active': True
        }
        if user.is_vet():
            qs2_params['user__groups__pk__in'] = User.IS_VET

        qs2 = self.helper(
            Activity.objects.filter(
                **qs2_params
            ).annotate(
                beacon=Value(
                    'upvote',
                    output_field=CharField()
                )
            ),
            user
        )

        qs3 = self.helper(
            Activity.objects.filter(
                post__user=user,
                action=Activity.COMMENT,
                active=True
            ).annotate(
                beacon=Value(
                    'comment', output_field=CharField()
                )
            ),
            user
        )

        qs4 = self.helper(
            Activity.objects.filter(
                post__in=user.likes.all(),
                action=Activity.COMMENT,
                active=True
            ).exclude(post__user=user).annotate(
                beacon=Value(
                    'like_comment',
                    output_field=CharField()
                )
            ),
            user
        )
        user_likes = list(
            UserLikesPost.objects.filter(
                post_id__in=[activity.post.id for activity in qs4],
                user=user
            ).select_related('post')
        )
        qs4 = list(qs4)
        qs5 = []
        for index, activity in enumerate(qs4):
            for like in user_likes:
                if like.post.id == activity.post.id:
                    if activity.updated_at > like.created_at:
                        # Only append the new ones after the like
                        qs5.append(activity)

        return sorted(
            chain(qs1, qs2, qs3, qs5),
            key=lambda instance: instance.updated_at,
            reverse=True
        )

    @staticmethod
    def helper(qs, user):
        return qs.exclude(user=user).select_related(
            *select_tuples
        ).prefetch_related(
            'post__images',
        )
