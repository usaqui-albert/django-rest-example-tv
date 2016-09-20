from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, Group
from django.db.models.signals import post_save

from .signals import create_auth_token

from .mixins import PermissionsMixin

VETERINARIAN_TYPES = (
    ('tech', 'Technician'),
    ('vet', 'Veterinarian'),
    ('student', 'Student')
)


class Group(Group):
    description = models.CharField(max_length=50)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    full_name = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_short_name(self):
        return self.full_name


# Func to connect the signal.
post_save.connect(
    create_auth_token, sender=User, dispatch_uid="users.models.user_post_save")


class Breeder(models.Model):
    breeder_type = models.CharField(max_length=100)
    bussiness_name = models.CharField(max_length=100)
    bussiness_website = models.URLField(null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = models.ForeignKey('countries.Country')
    state = models.ForeignKey('countries.State')
    verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Breeder"
        verbose_name_plural = "Breeders"

    def __unicode__(self):
        return u'%s %s' % (self.user.full_name, self.breeder_type)

    def save(self, *args, **kwargs):
        if self.country != self.state.country:
            raise ValueError(
                "The state provided is not from the country provided.")
        super(Breeder, self).save(self, *args, **kwargs)


class Veterinarian(models.Model):
    area_interest = models.CharField(max_length=150)
    veterinary_school = models.CharField(max_length=50)
    graduating_year = models.IntegerField()
    verified = models.BooleanField(default=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    veterinarian_type = models.CharField(
        choices=VETERINARIAN_TYPES, max_length=50)

    class Meta:
        verbose_name = "Veterinarian"
        verbose_name_plural = "Veterinarians"

    def __unicode__(self):
        return u'%s %s' % (self.user.full_name, self.veterinarian_type)
