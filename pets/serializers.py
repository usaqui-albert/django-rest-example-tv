from django.core.exceptions import ValidationError

from rest_framework import serializers

from .models import Pet


class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = (
            'user', 'name', 'fixed', 'image',
            'age', 'pet_type', 'breed', 'id', 'gender'
        )
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True}
        }

    def create(self, validated_data):
        if Pet.objects.filter(user=self.context['user']).count() > 19:
            raise ValidationError('Max 20 pets allowed!')
        pet = Pet(**dict(validated_data, user=self.context['user']))
        pet.save()
        return pet
