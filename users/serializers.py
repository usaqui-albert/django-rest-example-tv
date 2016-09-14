from rest_framework import serializers

from .models import User, Breeder


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
        read_only_fields = ('user')
