from django.contrib.auth import authenticate
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.serializers import (
    ValidationError, ModelSerializer, Serializer, BooleanField
)

from users.models import User
from users.serializers import (
    BreederSerializer, VeterinarianSerializer, ProfileImageSerializer
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
            'veterinarian', 'images', 'is_active'
        )


class AdminVerificationSerializer(Serializer):
    verified = BooleanField(write_only=True)
    locked = BooleanField(write_only=True)
