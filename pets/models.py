from __future__ import unicode_literals
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now


class Pet(models.Model):
    name = models.CharField(max_length=50)
    fixed = models.BooleanField(default=False)
    image = models.ImageField()
    age = models.IntegerField(
        validators=[
            MinValueValidator(now().year - 100),
            MaxValueValidator(now().year)
        ])

    class Meta:
        verbose_name = "Pet"
        verbose_name_plural = "Pets"

    def __str__(self):
        pass

    def save(self):
        pass

    @models.permalink
    def get_absolute_url(self):
        return ('')
