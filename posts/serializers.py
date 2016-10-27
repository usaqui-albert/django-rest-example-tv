from StringIO import StringIO
from PIL import Image as Img
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.serializers import (
    ModelSerializer, IntegerField, ImageField, ValidationError)

from .models import Post, ImagePost, PaymentAmount


class ImagePostSerializer(ModelSerializer):

    class Meta:
        model = ImagePost
        fields = ('id', 'standard', 'thumbnail')
        extra_kwargs = {
            'id': {'read_only': True}
        }


class PostSerializer(ModelSerializer):
    likes_count = IntegerField(read_only=True)
    images = ImagePostSerializer(many=True, read_only=True)
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
        image_2 = validated_data.pop('image_2', None)
        image_3 = validated_data.pop('image_3', None)
        if not (image_1):
            raise ValidationError('At least 1 image is required')
        post = Post(**dict(
            validated_data, user=self.context['user']))
        post.save()
        for image in [image_1, image_2, image_3]:
            if image:
                self.create_image_post(image, post)
        return post

    def image_with_background(self, img, size, output):
        '''
            Recieve the img and paste it on a white new image
            allowing to make a square image. offset variable, allowing
            to center the image.
        '''
        background = Img.new('RGB', size, 'white')
        offset = (size[0] - img.size[0]) / 2, (size[1] - img.size[1]) / 2
        background.paste(img, offset)
        background.save(output, format='JPEG', quality=70)
        output.seek(0)
        return output

    def image_no_background(self, img, size, output):
        '''
            Only save the image and change the output steam
        '''
        img.save(output, format='JPEG', quality=70)
        output.seek(0)
        return output

    def image_resize(self, size, img, image_stream):
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.thumbnail(size, Img.ANTIALIAS)
        '''
        Two choices:

        output = self.image_no_background(img, size, StringIO())

        Will return an image with no white background, this means that the
        image will no be a square image.

        output = self.image_with_background(img, size, StringIO())

        Will return  an image with a white background, making this a square
        image.

        This choices will be helpful in  near the future when the client see
        the feed frontend and choose one or the other.

        '''
        output = self.image_with_background(img, size, StringIO())
        image = InMemoryUploadedFile(
            output, 'ImageField', "%s.jpg" % image_stream.name.split('.')[0],
            'image/jpeg', output.len, None)
        return image

    def create_image_post(self, image_stream, post):
        '''
            This definition receive the image stream, make two image
            off the same steam, then create an imagePost instance and
            assign it to the post passed. Then the instance is saved
        '''
        img = Img.open(StringIO(image_stream.read()))
        img_copy = img.copy()
        standard = self.image_resize((612, 612), img, image_stream)
        thumbnail = self.image_resize((150, 150), img_copy, image_stream)
        image_post = ImagePost(
            standard=standard, thumbnail=thumbnail,
            post=post)
        image_post.save()


class PaymentAmountSerializer(ModelSerializer):
    class Meta:
        model = PaymentAmount
        fields = '__all__'
