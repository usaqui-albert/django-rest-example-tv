from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .serializers import AppTextSerializer
from .models import AppText


class AppTextView(ListAPIView):
    serializer_class = AppTextSerializer
    permission_classes = (AllowAny,)
    queryset = AppText.objects.all()
