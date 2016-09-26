from __future__ import unicode_literals
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now

PET_GENDER = (
    ('male', 'Male'),
    ('female', 'Female')
)


def get_current_year():
    '''
    Get the current year.
    '''
    return now().year


def get_limit_year():
    '''
    Get the current year minus 100.
    '''
    return now().year - 100


def uploads_path(instance, filename):
    '''
    Function to organize the upload directory
    this way, every file is organized by username and management
    is a lot faster
    '''
    return '/'.join(['uploads', instance.user.username, filename])


class Pet(models.Model):
    name = models.CharField(max_length=50)
    fixed = models.BooleanField(default=False)
    image = models.ImageField(null=True, blank=True, upload_to=uploads_path)
    age = models.IntegerField(
        validators=[
            MinValueValidator(get_current_year),
            MaxValueValidator(get_limit_year)
        ]
    )  # We just need the year, int is better optimized
    pet_type = models.CharField(max_length=150)  # Need the list to complete
    breed = models.CharField(max_length=150)  # Need the list to complete
    gender = models.CharField(choices=PET_GENDER, max_length=50)
    user = models.ForeignKey('users.User')  # 20 limit per user

    class Meta:
        verbose_name = "Pet"
        verbose_name_plural = "Pets"

    def __unicode__(self):
        return u"%s - %s" % (self.id, self.name)
