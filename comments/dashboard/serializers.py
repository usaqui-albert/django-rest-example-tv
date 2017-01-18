from rest_framework.serializers import ModelSerializer, CharField

from users.serializers import UserSerializers
from users.dashboard.serializers import AdminUserSerializer
from posts.serializers import PostSmallSerializer

from ..models import Feedback


class AdminFeedbackListSerializer(ModelSerializer):
    veterinarian = AdminUserSerializer(
        read_only=True, source="comment.user")
    full_name = CharField(source='user.full_name')

    class Meta:
        model = Feedback
        fields = (
            'comment', 'user', 'was_helpful', 'description',
            'id', 'veterinarian', 'full_name'
        )


class AdminFeedbackSerializer(ModelSerializer):
    veterinarian = AdminUserSerializer(
        read_only=True, source="comment.user")
    user = UserSerializers(read_only=True)
    post = PostSmallSerializer(source='comment.post')
    comment_description = CharField(
        read_only=True, source="comment.description")

    class Meta:
        model = Feedback
        fields = (
            'comment', 'was_helpful', 'description',
            'id', 'veterinarian', 'user', 'post', 'comment_description'
        )
