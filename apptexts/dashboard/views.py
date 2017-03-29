from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAdminUser

from ..serializers import AppTextSerializer
from ..models import AppText


class AdminAppTextView(ListAPIView):
    serializer_class = AppTextSerializer
    permission_classes = (IsAdminUser,)
    queryset = AppText.objects.all()


class AdminAppTextDetailView(RetrieveUpdateAPIView):
    serializer_class = AppTextSerializer
    permission_classes = (IsAdminUser,)
    queryset = AppText.objects.all()
