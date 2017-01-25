from django.db import models


class AppText(models.Model):
    key = models.CharField(max_length=100)
    description = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
