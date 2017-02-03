from django.contrib.auth import authenticate
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.serializers import (
    ValidationError, ModelSerializer, Serializer, BooleanField
)

from users.models import User
from users.serializers import (
    BreederSerializer, VeterinarianSerializer, ProfileImageSerializer,
    UserUpdateSerializer
)


class AdminAuthTokenSerializer(AuthTokenSerializer):

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                if not user.is_active:
                    msg = 'User account is disabled.'
                    raise ValidationError(msg)
                if not user.is_staff:
                    msg = 'You need valid staff permissions.'
                    raise ValidationError(msg)
            else:
                msg = 'Unable to log in with provided credentials.'
                raise ValidationError(msg)
        else:
            msg = 'Must include "username" and "password".'
            raise ValidationError(msg)

        attrs['user'] = user
        return attrs


class AdminUserSerializer(ModelSerializer):
    breeder = BreederSerializer(required=False)
    veterinarian = VeterinarianSerializer(required=False)
    images = ProfileImageSerializer(read_only=True, source='image')

    class Meta:
        model = User
        fields = (
            'username', 'email', 'full_name', 'groups', 'id', 'breeder',
            'veterinarian', 'images', 'is_active', 'is_staff', 'created_at'
        )


class AdminUserUpdateSerializer(ModelSerializer):
    breeder = BreederSerializer(required=False)
    veterinarian = VeterinarianSerializer(required=False)

    class Meta:
        model = User
        fields = (
            'full_name', 'veterinarian', 'breeder'
        )

    def update(self, instance, validated_data):
        breeder_data = validated_data.pop('breeder', None)
        veterinarian_data = validated_data.pop('veterinarian', None)

        if instance.groups.id == 2 and breeder_data:
            if hasattr(instance, 'breeder'):
                serializer = BreederSerializer(
                    instance.breeder,
                    data=breeder_data,
                    partial=True
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()

        elif instance.groups.id in [3, 4, 5] and veterinarian_data:
            if hasattr(instance, 'veterinarian'):
                serializer = VeterinarianSerializer(
                    instance.veterinarian,
                    data=veterinarian_data,
                    partial=True
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    @staticmethod
    def validate_veterinarian(value):
        return UserUpdateSerializer.validate_veterinarian(value)

    @staticmethod
    def validate_breeder(value):
        return UserUpdateSerializer.validate_breeder(value)


class AdminVerificationSerializer(Serializer):
    verified = BooleanField(write_only=True)
    locked = BooleanField(write_only=True)
