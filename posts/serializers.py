import StringIO
from copy import deepcopy
from PIL import Image as Img
from django.core.files import uploadedfile  #InMemoryUploadedFile
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


class PostPetOwnerSerializer(ModelSerializer):
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
        image_1 = validated_data.pop('image_1', None)
        # image_2 = validated_data.pop('image_2', None)
        # image_3 = validated_data.pop('image_3', None)
        post = Post(**dict(
            validated_data, user=self.context['user']))
        post.save()
        if image_1:
            # image_t = deepcopy(image_1)
            image_t = self.image_resize((612, 612), image_1)
            image_1 = ImagePost(
                standard=image_t,
                post=post)
            image_1.save()
        return post

    def image_resize(self, size, image):
        img = Img.open(StringIO.StringIO(image.read()))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.thumbnail(size, Img.ANTIALIAS)
        output = StringIO.StringIO()
        # background = Img.new('RGB', size, (255, 255, 255))
        # offset = (((size[0] - img.size[0]) / 2), ((size[1] - img.size[1]) / 2))
        # background.paste(
        #     im=image, box=offset
        # )
        # background.save(output, format='JPEG', quality=70)
        img.save(output, format='JPEG', quality=70)
        output.seek(0)
        image = uploadedfile.InMemoryUploadedFile(
            output, 'ImageField', "%s.jpg" % image.name.split('.')[0],
            'image/jpeg', output.len, None)

        return image
