from django.contrib.auth import authenticate
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.serializers import ValidationError


class AdminAuthTokenSerializer(AuthTokenSerializer):

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                if not user.is_active:
                    msg = 'User account is disabled.'
                    raise ValidationError(msg, code='authorization')
                if not user.is_staff:
                    msg = 'You need valid staff permissions.'
                    raise ValidationError(msg, code='authorization')
            else:
                msg = 'Unable to log in with provided credentials.'
                raise ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "username" and "password".'
            raise ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
