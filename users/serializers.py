from PIL import Image as Img
from StringIO import StringIO

from django.db import IntegrityError
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.serializers import (
    ModelSerializer, ValidationError, ImageField, Serializer, EmailField,
    CharField, SerializerMethodField, IntegerField, BooleanField, ChoiceField
)
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer

from TapVet.images import ImageSerializerMixer, STANDARD_SIZE, THUMBNAIL_SIZE

from .models import (
    User, Breeder, Veterinarian, AreaInterest, ProfileImage)
from .mixins import Group


class SettingsMixerSerializer:

    @staticmethod
    def get_settings(obj):
        return {
            'blur_images': obj.blur_images,
            'interested_notification': obj.interested_notification,
            'vet_reply_notification': obj.vet_reply_notification,
            'comments_notification': obj.comments_notification,
            'comments_like_notification': obj.comments_like_notification
        }


class CreateUserSerializer(ModelSerializer, SettingsMixerSerializer):
    """Serializer to handle the creation of a user"""
    settings = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'password', 'username', 'email', 'full_name', 'groups', 'id',
            'settings'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
            'groups': {'required': True}
        }

    @staticmethod
    def validate_full_name(value):
        """Method to validate the full name field (example to do some tests)

        :param value:
        :return:
        """
        if len(value) < 0:
            raise ValidationError(
                'Invalid full name, should be longer than zero characters')
        return value

    @staticmethod
    def validate_password(value):
        """Method to validate the password field (example to do some tests)

        :param value:
        :return:
        """
        if len(value) < 1:
            raise ValidationError(
                'Invalid password, should not be empty')
        return value

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(user.password)
        user.save()
        return user


class ProfileImageSerializer(ModelSerializer):
    class Meta:
        model = ProfileImage
        fields = ('id', 'standard', 'thumbnail')
        extra_kwargs = {
            'user': {'read_only': True},
            'id': {'read_only': True},
        }


class UserSerializers(ModelSerializer):
    image = ProfileImageSerializer(read_only=True)
    label = CharField(source='get_label', read_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'full_name', 'groups', 'id', 'image',
            'label'
        )
        extra_kwargs = {
            'username': {'read_only': True},
            'id': {'read_only': True},
        }


class BreederSerializer(ModelSerializer):
    class Meta:
        model = Breeder
        fields = (
            'user', 'breeder_type', 'business_name', 'business_website',
            'country', 'state', 'id'
        )
        read_only_fields = ('user', 'id')

    def create(self, validated_data):
        breeder = Breeder(**dict(validated_data, user=self.context['user']))
        breeder.save()
        return breeder


class VeterinarianSerializer(ModelSerializer):
    class Meta:
        model = Veterinarian
        fields = (
            'user', 'area_interest', 'veterinary_school', 'graduating_year',
            'verified', 'veterinarian_type', 'id', 'country', 'state',
            'locked', 'license_number'
        )
        read_only_fields = ('user', 'id', 'locked', 'verified')

    def create(self, validated_data):
        veterinarian = Veterinarian(
            **dict(validated_data, user=self.context['user']))
        veterinarian.change_status().save()
        return veterinarian

    def save(self, **kwargs):
        '''
        We need to overwrite this method, to allow m2m keys on area of interest
        '''
        validated_data = dict(
            list(self.validated_data.items()) +
            list(kwargs.items())
        )
        if self.instance:
            request_user = self.context['user']
            if self.instance.user.id == request_user.id:
                self.instance.change_status()
            self.instance = self.update(self.instance, validated_data)
        else:
            area_interest = validated_data.pop('area_interest', [])
            self.instance = self.create(validated_data)
            if area_interest:
                self.instance.area_interest.set(area_interest)

        return self.instance


class GroupsSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'description')
        read_only_fields = ('id', 'name', 'description')


class AreaInterestSerializer(ModelSerializer):
    class Meta:
        model = AreaInterest
        fields = ('id', 'name')
        extra_kwargs = {
            'id': {'read_only': True},
            'name': {'read_only': True}
        }


class UserOwnerVetSerializer(ModelSerializer):
    follows_count = IntegerField(read_only=True)
    followed_by_count = IntegerField(read_only=True)
    comments_count = IntegerField(read_only=True)
    interest_count = IntegerField(read_only=True)
    upvotes_count = IntegerField(read_only=True)
    label = CharField(source='get_label', read_only=True)
    full_name = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'full_name', 'id',
            'follows_count', 'followed_by_count',
            'comments_count', 'interest_count', 'upvotes_count', 'label'
        )
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {'read_only': True},
            'user': {'read_only': True},
            'groups': {'read_only': True},
            'verified': {'read_only': True},
        }

    @staticmethod
    def get_full_name(obj):
        return 'Veterinary Professional #%s' % (1000 + obj.id)


class UserUpdateSerializer(
    ModelSerializer, ImageSerializerMixer, SettingsMixerSerializer
):
    breeder = BreederSerializer(required=False)
    veterinarian = VeterinarianSerializer(required=False)
    image = ImageField(write_only=True, required=False)
    images = ProfileImageSerializer(read_only=True, source='image')
    follows_count = IntegerField(read_only=True)
    followed_by_count = IntegerField(read_only=True)
    comments_count = IntegerField(read_only=True)
    interest_count = IntegerField(read_only=True)
    upvotes_count = IntegerField(read_only=True)
    followed = BooleanField(read_only=True)
    label = CharField(source='get_label', read_only=True)
    settings = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'full_name', 'groups', 'id', 'followed',
            'breeder', 'veterinarian', 'image', 'images', 'blur_images',
            'interested_notification', 'vet_reply_notification',
            'comments_notification', 'comments_like_notification',
            'follows_count', 'followed_by_count', 'comments_count',
            'interest_count', 'upvotes_count', 'label', 'settings'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
            'username': {'read_only': True},
            'user': {'read_only': True},
            'groups': {'read_only': True},
            'verified': {'read_only': True},
            'interested_notification': {'write_only': True},
            'vet_reply_notification': {'write_only': True},
            'comments_notification': {'write_only': True},
            'comments_like_notification': {'write_only': True},
            'blur_images': {'write_only': True}
        }

    def update(self, instance, validated_data):
        breeder_data = validated_data.pop('breeder', None)
        veterinarian_data = validated_data.pop('veterinarian', None)
        image = validated_data.pop('image', None)

        if instance.groups.id == 2:
            if breeder_data:
                if hasattr(instance, 'breeder'):
                    serializer = BreederSerializer(
                        instance.breeder,
                        data=breeder_data,
                        partial=True
                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                else:
                    serializer = BreederSerializer(
                        data=breeder_data,
                        context=self.context
                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
        elif instance.groups.id in User.IS_VET:
            if veterinarian_data:
                if hasattr(instance, 'veterinarian'):
                    serializer = VeterinarianSerializer(
                        instance.veterinarian,
                        data=veterinarian_data,
                        partial=True,
                        context=self.context
                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                else:
                    serializer = VeterinarianSerializer(
                        data=veterinarian_data,
                        context=self.context
                    )
                    serializer.is_valid(raise_exception=True)
                    try:
                        serializer.save()
                    except (
                        IntegrityError,
                        ValueError,
                        DjangoValidationError
                    ) as err:
                        raise ValidationError({'veterinarian': str(err)})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if image:

            try:
                old_image = instance.image
                old_image.delete()
            except:
                pass

            self.create_image_profile(image, instance)
        return instance

    def create_image_profile(self, image_stream, user):
        '''
            This definition receive the image stream, make two image
            off the same steam, then create an ProfileImage instance and
            assign it to the user passed. Then the instance is saved
        '''
        img = Img.open(StringIO(image_stream.read()))
        img_copy = img.copy()
        standard = self.image_resize(STANDARD_SIZE, img, image_stream)
        thumbnail = self.image_resize(THUMBNAIL_SIZE, img_copy, image_stream)
        profile_image = ProfileImage(
            standard=standard, thumbnail=thumbnail,
            user=user)
        profile_image.save()

    @staticmethod
    def validate_veterinarian(value):
        if 'area_interest' in value:
            areas = value['area_interest']
            value['area_interest'] = [area.id for area in areas]
        if 'country' in value:
            value['country'] = value['country'].id
        if 'state' in value:
            value['state'] = value['state'].id
        return value

    @staticmethod
    def validate_breeder(value):
        if 'country' in value:
            value['country'] = value['country'].id
        if 'state' in value:
            value['state'] = value['state'].id
        return value


class ReferFriendSerializer(Serializer):
    email = EmailField(max_length=100)


class TokenSerializer(ModelSerializer):
        class Meta:
            model = Token
            fields = ('key',)
            extra_kwargs = {
                'key': {'read_only': True},
            }


class UserLoginSerializer(ModelSerializer, SettingsMixerSerializer):
    image = ProfileImageSerializer(read_only=True)
    label = CharField(source='get_label', read_only=True)
    token = CharField(source="auth_token.key", read_only=True)
    settings = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'full_name', 'email', 'groups', 'created_at',
            'stripe_token', 'image', 'label', 'token', 'settings',
            'created_at'
        )


class UserFollowsSerializer(UserSerializers):
    following = BooleanField(read_only=True)
    label = CharField(source='get_label', read_only=True)

    class Meta(UserSerializers.Meta):
        fields = UserSerializers.Meta.fields + ('following',)


class EmailToResetPasswordSerializer(Serializer):
    email = EmailField(write_only=True)

    @staticmethod
    def validate_email(value):
        user = User.objects.filter(email=value).first()
        if user:
            return user
        raise ValidationError('Email not registered.')


class RestorePasswordSerializer(Serializer):
    verification_code = CharField(max_length=6, write_only=True, min_length=6)
    new_password = CharField(write_only=True)
    confirm_password = CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise ValidationError('Passwords do not match.')
        return attrs


class AuthTokenMailSerializer(AuthTokenSerializer):
    email = EmailField(label="Email", required=False)
    username = CharField(label="Username", required=False)
    msg = 'Unable to log in with provided credentials.'
    msg_email_pass = 'Must include "email" and "password".'
    msg_username_pass = 'Must include "username" and "password".'

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        email = attrs.get('email')
        if email:
            if email and password:
                qs = User.objects.filter(
                    email=email).values('username').first()
                if qs:
                    username = qs.get('username', None)
                    user = authenticate(username=username, password=password)
                    if not user:
                        raise ValidationError(self.msg, code='authorization')
                else:
                    raise ValidationError(self.msg, code='authorization')

            else:
                raise ValidationError(
                    self.msg_email_pass, code='authorization'
                )
        else:
            if username and password:
                user = authenticate(username=username, password=password)

                if not user:
                    raise ValidationError(self.msg, code='authorization')

            else:
                raise ValidationError(
                    self.msg_username_pass, code='authorization')

        attrs['user'] = user
        return attrs


class DeviceSerializer(Serializer):
    IOS = 'ios'
    ANDROID = 'android'
    PLATFORMS = (IOS, ANDROID)

    device_token = CharField(max_length=255)
    platform = ChoiceField(choices=PLATFORMS)
