from rest_framework import serializers
from django.contrib.auth.models import Group

from .models import User, Breeder, Veterinarian


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer to handle the creation of a user"""
    class Meta:
        model = User
        fields = ('password', 'username', 'email', 'full_name', 'groups')

    @staticmethod
    def validate_full_name(value):
        """Method to validate the full name field (example to do some tests)

        :param value:
        :return:
        """
        if len(value) < 5:
            raise serializers.ValidationError(
                'Invalid fullname, should be longer than 5 characters')
        return value

    @staticmethod
    def validate_password(value):
        """Method to validate the password field (example to do some tests)

        :param value:
        :return:
        """
        if len(value) < 8:
            raise serializers.ValidationError(
                'Invalid password, should be longer than 8 characters')
        return value


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'groups')


class BreederSerializer(serializers.ModelSerializer):
    class Meta:
        model = Breeder
        fields = (
            'user', 'breeder_type', 'bussiness_name', 'business_website',
            'country', 'state', 'verified'
        )
        read_only_fields = ('user',)

    def create(self, validated_data, **kwargs):
        breeder = Breeder(
            user=kwargs['user'],
            breeder_type=validated_data['breeder_type'],
            bussiness_name=validated_data['bussiness_name'],
            country=validated_data['country'],
            state=validated_data['state']
        )
        breeder.save()
        return breeder

    def save(self, **kwargs):
        assert not hasattr(self, 'save_object'), (
            'Serializer `%s.%s` has old-style version 2 `.save_object()` '
            'that is no longer compatible with REST framework 3. '
            'Use the new-style `.create()` and `.update()` methods instead.' %
            (self.__class__.__module__, self.__class__.__name__)
        )

        assert hasattr(self, '_errors'), (
            'You must call `.is_valid()` before calling `.save()`.'
        )

        assert not self.errors, (
            'You cannot call `.save()` on a serializer with invalid data.'
        )

        # Guard against incorrect use of `serializer.save(commit=False)`
        assert 'commit' not in kwargs, (
            "'commit' is not a valid keyword argument to the 'save()' method. "
            "If you need to access data before committing to the database then "
            "inspect 'serializer.validated_data' instead. "
            "You can also pass additional keyword arguments to 'save()' if you "
            "need to set extra attributes on the saved model instance. "
            "For example: 'serializer.save(owner=request.user)'.'"
        )

        assert not hasattr(self, '_data'), (
            "You cannot call `.save()` after accessing `serializer.data`."
            "If you need to access data before committing to the database then "
            "inspect 'serializer.validated_data' instead. "
        )

        validated_data = dict(
            list(self.validated_data.items()) +
            list(kwargs.items())
        )

        if self.instance is not None:
            self.instance = self.update(self.instance, validated_data)
            assert self.instance is not None, (
                '`update()` did not return an object instance.'
            )
        else:
            self.instance = self.create(validated_data, **kwargs)
            assert self.instance is not None, (
                '`create()` did not return an object instance.'
            )

        return self.instance

class VeterinarianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veterinarian
        fields = (
            'area_interest', 'veterinary_school', 'graduating_year',
            'verified', 'user', 'veterinarian_type'
        )


class GroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')
