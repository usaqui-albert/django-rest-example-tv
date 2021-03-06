from rest_framework.serializers import (
    ModelSerializer, IntegerField, CharField, BooleanField,
    SerializerMethodField, NullBooleanField)

from users.serializers import ProfileImageSerializer, UserSerializers


from .models import Comment, Feedback


class CommentSerializer(ModelSerializer):
    upvoters_count = IntegerField(read_only=True)
    label = CharField(source='user.get_label', read_only=True)
    full_name = CharField(source='user.full_name', read_only=True)
    username = CharField(source='user.username', read_only=True)
    upvoted = BooleanField(read_only=True)
    image = ProfileImageSerializer(source='user.image', read_only=True)
    user_id = IntegerField(read_only=True, source='user.id')

    class Meta:
        model = Comment
        fields = (
            'description', 'id', 'user', 'post', 'created_at', 'updated_at',
            'upvoters_count', 'label', 'full_name', 'upvoted', 'image',
            'username', 'user_id'
        )
        extra_kwargs = {
            'user': {'read_only': True},
            'post': {'read_only': True}
        }

    def create(self, validated_data):
        comment = Comment(**dict(validated_data, user=self.context['user']))
        comment.save()
        return comment


class CommentVetSerializer(CommentSerializer):
    has_feedback = BooleanField(read_only=True)

    class Meta:
        model = Comment
        fields = (
            'description', 'id', 'post', 'created_at', 'updated_at',
            'upvoters_count', 'label', 'full_name', 'upvoted', 'has_feedback',
            'image', 'username', 'user_id'
        )
        extra_kwargs = {
            'user': {'read_only': True},
            'post': {'read_only': True}
        }


class CommentVetNamelessSerializer(CommentVetSerializer):
    full_name = SerializerMethodField(read_only=True)
    image = SerializerMethodField(read_only=True)
    username = SerializerMethodField(
        read_only=True, method_name='get_full_name'
    )

    @staticmethod
    def get_full_name(obj):
        return 'Veterinary Professional #%s' % (1000 + obj.user.id)

    @staticmethod
    def get_image(obj):
        return None


class FeedbackSerializer(ModelSerializer):
    was_helpful = NullBooleanField(required=True)
    user = UserSerializers(required=False)

    class Meta:
        model = Feedback
        fields = ('was_helpful', 'description', 'user')
        extra_kwargs = {
            'was_helpful': {'required': True, 'allow_null': False},
            'user': {'read_only': True}
        }

    def create(self, validated_data):
        feedback = Feedback(
            **dict(
                validated_data,
                user=self.context['user'],
                comment=self.context['comment']
            )
        )
        feedback.save()
        return feedback
