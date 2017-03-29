from rest_framework.serializers import (
    ModelSerializer, ValidationError, CharField)

from .models import Pet, PetType


class PetSerializer(ModelSerializer):
    pet_type_name = CharField(read_only=True, source="pet_type")

    class Meta:
        model = Pet
        fields = (
            'user', 'name', 'fixed', 'image',
            'birth_year', 'pet_type', 'breed', 'id', 'gender',
            'pet_type_name'
        )
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True},
            'image': {'read_only': True}
        }

    def create(self, validated_data):
        if Pet.objects.filter(user=self.context['user']).count() > 19:
            raise ValidationError('Max 20 pets allowed!')
        pet = Pet(**dict(validated_data, user=self.context['user']))
        pet.save()
        return pet


class PetTypeSerializer(ModelSerializer):

    class Meta:
        model = PetType
        fields = ('id', 'name')
        extra_kwargs = {
            'id': {'read_only': True}
        }
