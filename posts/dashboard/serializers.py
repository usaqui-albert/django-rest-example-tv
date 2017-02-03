from rest_framework.serializers import ModelSerializer, BooleanField

from ..models import Post
from ..serializers import ImagePostSerializer
from users.serializers import UserSerializers


class AdminPostSerializer(ModelSerializer):
    images = ImagePostSerializer(many=True, read_only=True)
    user = UserSerializers(read_only=True)
    is_paid = BooleanField(read_only=True)

    class Meta:
        model = Post
        fields = (
            'id', 'description', 'images', 'is_paid', 'user',
            'created_at', 'active', 'visible_by_vet', 'visible_by_owner'
        )
        extra_kwargs = {
            'description': {'read_only': True},
            'is_paid': {'read_only': True},
            'created_at': {'read_only': True}
        }
