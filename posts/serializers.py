from StringIO import StringIO
from PIL import Image as Img
from rest_framework.serializers import (
    ModelSerializer, IntegerField, ImageField, ValidationError, BooleanField)

from TapVet.images import ImageSerializerMixer, STANDARD_SIZE, THUMBNAIL_SIZE
from users.serializers import UserSerializers

from .models import Post, ImagePost, PaymentAmount


class ImagePostSerializer(ModelSerializer):

    class Meta:
        model = ImagePost
        fields = ('id', 'standard', 'thumbnail')
        extra_kwargs = {
            'id': {'read_only': True}
        }


class PostSerializer(ModelSerializer, ImageSerializerMixer):
    likes_count = IntegerField(read_only=True)
    vet_comments = IntegerField(read_only=True)
    owner_comments = IntegerField(read_only=True)
    images = ImagePostSerializer(many=True, read_only=True)
    image_1 = ImageField(write_only=True, required=False)
    image_2 = ImageField(write_only=True, required=False)
    image_3 = ImageField(write_only=True, required=False)
    user_detail = UserSerializers(read_only=True, source='user')
    interested = BooleanField(read_only=True)

    class Meta:
        model = Post
        fields = (
            'description', 'pet', 'user', 'id', 'likes_count', 'images',
            'image_1', 'image_2', 'image_3', 'vet_comments', 'owner_comments',
            'created_at', 'user_detail', 'interested'
        )
        extra_kwargs = {
            'user': {'read_only': True},
            'id': {'read_only': True},
        }

    def create(self, validated_data):
        image_1 = validated_data.pop('image_1', None)
        image_2 = validated_data.pop('image_2', None)
        image_3 = validated_data.pop('image_3', None)
        if not (image_1):
            raise ValidationError('At least 1 image is required')
        post = Post(**dict(
            validated_data, user=self.context['user']))
        post.save()
        for index, image in enumerate([image_1, image_2, image_3], start=1):
            if image:
                self.create_image_post(image, post, index)
        return post

    def update(self, instance, validated_data):
        image_1 = validated_data.pop('image_1', None)
        image_2 = validated_data.pop('image_2', None)
        image_3 = validated_data.pop('image_3', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        for index, new_image in enumerate(
            [image_1, image_2, image_3], start=1
        ):
            if new_image:
                image = instance.images.filter(image_number=index).first()
                if image:
                    image.delete()
                self.create_image_post(new_image, instance, index)
        return instance

    def create_image_post(self, image_stream, post, index):
        '''
            This definition receive the image stream, make two image
            off the same steam, then create an imagePost instance and
            assign it to the post passed. Then the instance is saved,
        '''
        img = Img.open(StringIO(image_stream.read()))
        img_copy = img.copy()
        standard = self.image_resize(STANDARD_SIZE, img, image_stream)
        thumbnail = self.image_resize(THUMBNAIL_SIZE, img_copy, image_stream)
        image_post = ImagePost(
            standard=standard, thumbnail=thumbnail,
            post=post, image_number=index)
        image_post.save()


class PaymentAmountSerializer(ModelSerializer):

    class Meta:
        model = PaymentAmount
        fields = '__all__'


class PaidPostSerializer(ModelSerializer):
    images = ImagePostSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            'description', 'pet', 'id', 'images'
        )
        extra_kwargs = {
            'id': {'read_only': True},
        }
