from rest_framework.serializers import ModelSerializer, IntegerField

from .models import Comment


class CommentSerializer(ModelSerializer):
    upvoters_count = IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = (
            'description', 'id', 'user', 'post', 'created_at', 'updated_at',
            'upvoters_count')
        extra_kwargs = {
            'user': {'read_only': True},
            'post': {'read_only': True},
        }

    def create(self, validated_data):
        comment = Comment(**dict(validated_data, user=self.context['user']))
        comment.save()
        return comment
