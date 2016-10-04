from rest_framework import serializers

from .models import Pet, PetType


class PetSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Pet
        fields = (
            'user', 'name', 'fixed', 'image',
            'birth_year', 'pet_type', 'breed', 'id', 'gender',
            'image_url'
        )
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True},
            'image': {'read_only': True},
            'image_url': {'read_only': True}
        }

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        else:
            return None

    def create(self, validated_data):
        if Pet.objects.filter(user=self.context['user']).count() > 19:
            raise serializers.ValidationError('Max 20 pets allowed!')
        pet = Pet(**dict(validated_data, user=self.context['user']))
        pet.save()
        return pet


class PetTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PetType
        fields = ('id', 'name')
        extra_kwargs = {
            'id': {'read_only': True}
        }
