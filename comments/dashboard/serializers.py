from rest_framework.serializers import ModelSerializer, CharField

from users.dashboard.serializers import AdminUserSerializer

from ..models import Feedback


class AdminFeedbackSerializer(ModelSerializer):
    veterinarian = AdminUserSerializer(
        read_only=True, source="comment.user")
    full_name = CharField(source='user.full_name')

    class Meta:
        model = Feedback
        fields = (
            'comment', 'user', 'was_helpful', 'description',
            'id', 'veterinarian', 'full_name'
        )
