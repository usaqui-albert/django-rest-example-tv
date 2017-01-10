from rest_framework.serializers import ModelSerializer

from ..models import Post
from ..serializers import ImagePostSerializer
from users.serializers import UserSerializers


class AdminPostSerializer(ModelSerializer):
    images = ImagePostSerializer(many=True, read_only=True)
    user = UserSerializers(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'description', 'images', 'is_paid', 'user',
                  'created_at', 'active')


class AdminPostActiveDeactiveSerializer(ModelSerializer):

    class Meta:
        model = Post
        fields = ('active',)
