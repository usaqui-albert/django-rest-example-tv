from rest_framework import serializers
from .models import User


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer to handle the creation of a user"""
    class Meta:
        model = User
        fields = '__all__'

    @staticmethod
    def validate_full_name(value):
        """

        :param value:
        :return:
        """
        if len(value) < 5:
            raise serializers.ValidationError(
                'Invalid fullname, should be longer than 10 characters')
        return value

    @staticmethod
    def validate_password(value):
        """

        :param value:
        :return:
        """
        if len(value) < 8:
            raise serializers.ValidationError(
                'Invalid password, should be longer than 8 characters')
        return value
