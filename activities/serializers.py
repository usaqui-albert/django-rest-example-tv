from rest_framework.serializers import ModelSerializer, CharField

from posts.serializers import PostSmallSerializer
from users.serializers import UserSerializers
from comments.serializers import CommentSerializer
from .models import Activity


class ActivitySerializer(ModelSerializer):
    post = PostSmallSerializer()
    user = UserSerializers()
    comment = CommentSerializer()
    follows = UserSerializers()
    beacon = CharField()

    class Meta:
        model = Activity
        fields = (
            'user', 'action', 'post', 'comment', 'follows', 'created_at',
            'updated_at', 'beacon'
        )
