from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db.models.signals import post_save

from pets.models import get_current_year, get_limit_year

from .signals import create_auth_token, new_breeder_signal, new_vet_signal
from .mixins import PermissionsMixin


#  The Vet type code is now the same id of the group it represents
VETERINARIAN_TYPES = (
    ('3', 'Veterinarian'),
    ('4', 'Student'),
    ('5', 'Technician')
)


class AreaInterest(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ('id',)

    def __unicode__(self):
        return u'%s - %s' % (self.id, self.name)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    full_name = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    stripe_token = models.CharField(max_length=100, null=True, blank=True)
    add_paid_post = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_short_name(self):
        return self.full_name

    def is_vet(self):
        return self.groups.id in [3, 4, 5]


# Func to connect the signal on post save.
post_save.connect(
    create_auth_token, sender=User, dispatch_uid="users.models.user_post_save")


class Breeder(models.Model):
    breeder_type = models.CharField(max_length=100)
    business_name = models.CharField(max_length=100)
    business_website = models.URLField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = models.ForeignKey('countries.Country')
    state = models.ForeignKey('countries.State')

    class Meta:
        verbose_name = "Breeder"
        verbose_name_plural = "Breeders"

    def __unicode__(self):
        return u'%s %s' % (self.user.full_name, self.breeder_type)

    def save(self, *args, **kwargs):
        if self.country != self.state.country:
            raise ValueError(
                "The state provided is not from the country provided.")
        super(Breeder, self).save(*args, **kwargs)


# Func to connect the signal on post save.
post_save.connect(
    new_breeder_signal, sender=Breeder,
    dispatch_uid="users.models.breeder_post_save")


class Veterinarian(models.Model):
    area_interest = models.ManyToManyField(AreaInterest)
    veterinary_school = models.CharField(max_length=50)
    graduating_year = models.IntegerField()
    verified = models.BooleanField(default=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    veterinarian_type = models.CharField(
        choices=VETERINARIAN_TYPES, max_length=50)
    country = models.ForeignKey('countries.Country', blank=True, null=True)
    state = models.ForeignKey('countries.State', blank=True, null=True)

    class Meta:
        verbose_name = "Veterinarian"
        verbose_name_plural = "Veterinarians"

    def __unicode__(self):
        return u'%s %s' % (self.user.full_name, self.veterinarian_type)

    def save(self, *args, **kwargs):
        if self.veterinarian_type != '4':
            if self.graduating_year > get_current_year():
                raise ValueError(
                    'The graduating year cannot be higher than ' +
                    'the current year')
            if self.graduating_year < get_limit_year():
                raise ValueError(
                    'The graduating year cannot be lower than ' +
                    str(get_limit_year()))
            if self.country is None or self.state is None:
                raise ValidationError(
                    "Country and state are required"
                )
            if self.country != self.state.country:
                raise ValueError(
                    "The state provided is not from the country provided.")
        else:
            if self.graduating_year < get_limit_year():
                raise ValueError(
                    'The graduating year cannot be lower than ' +
                    str(get_limit_year()))
            if self.graduating_year > get_current_year() + 20:
                raise ValueError(
                    'The graduating year cannot be higher than ' +
                    'the year ' + str(get_current_year() + 20))
        super(Veterinarian, self).save(*args, **kwargs)


# Func to connect the signal on post save.
post_save.connect(
    new_vet_signal, sender=Veterinarian,
    dispatch_uid="users.models.veterinarian_post_save")
