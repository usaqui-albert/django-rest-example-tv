from rest_framework.serializers import ModelSerializer

from .models import AppText


class AppTextSerializer(ModelSerializer):
    class Meta:
        model = AppText
        fields = '__all__'
