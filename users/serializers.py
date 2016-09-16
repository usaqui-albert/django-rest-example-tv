from rest_framework import serializers
from django.contrib.auth.models import Group

from .models import User, Breeder, Veterinarian


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer to handle the creation of a user"""
    class Meta:
        model = User
        fields = ('password', 'username', 'email', 'full_name', 'groups', 'id')
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True}
        }

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

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(user.password)
        user.save()
        return user


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'groups', 'id')
        extra_kwargs = {
            'username': {'read_only': True},
            'id': {'read_only': True},
        }


class BreederSerializer(serializers.ModelSerializer):
    class Meta:
        model = Breeder
        fields = (
            'user', 'breeder_type', 'bussiness_name', 'bussiness_website',
            'country', 'state', 'verified'
        )
        read_only_fields = ('user',)

    def create(self, validated_data):
        breeder = Breeder(**dict(validated_data, user=self.context['user']))
        breeder.save()
        return breeder


class VeterinarianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veterinarian
        fields = (
            'user', 'area_interest', 'veterinary_school', 'graduating_year',
            'verified', 'veterinarian_type'
        )
        read_only_fields = ('user',)

    def create(self, validated_data):
        veterinarian = Veterinarian(
            **dict(validated_data, user=self.context['user']))
        veterinarian.save()
        return veterinarian


class GroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')
