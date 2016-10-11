from rest_framework.serializers import (
    ModelSerializer, IntegerField, ImageField)

from .models import Post, ImagePost


class ImagePostSerilizers(ModelSerializer):

    class Meta:
        model = ImagePost
        fields = ('id', 'standard', 'thumbnail')
        extra_kwargs = {
            'id': {'read_only': True}
        }


class PostVetSerializer(ModelSerializer):
    likes_count = IntegerField(read_only=True)
    images = ImagePostSerilizers(many=True, read_only=True)
    image_1 = ImageField(write_only=True, required=False)
    image_2 = ImageField(write_only=True, required=False)
    image_3 = ImageField(write_only=True, required=False)

    class Meta:
        model = Post
        fields = (
            'description', 'pet', 'user', 'id', 'likes_count', 'images',
            'image_1', 'image_2', 'image_3'
        )
        extra_kwargs = {
            'user': {'read_only': True},
            'id': {'read_only': True},
        }

    def create(self, validated_data):
        user = self.context['user']
        vet = False
        pet_owner = True

        if user.groups in [3, 4, 5]:
            vet = True and user.veterinarian.verified
            pet_owner = False

        post = Post(**dict(
            validated_data, user=user, visible_by_vet=vet,
            visible_by_owner=pet_owner))
        post.save()
        return post
