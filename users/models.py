from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager

from .mixins import PermissionsMixin

VETERINARIAN_TYPES = (
    ('tech', 'Technician'),
    ('vet', 'Veterinarian'),
    ('student', 'Student')
)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    full_name = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)
    # is_superuser = models.BooleanField(default=False)
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


class Breeder(models.Model):
    breeder_type = models.CharField(max_length=100)
    bussiness_name = models.CharField(max_length=100)
    business_website = models.URLField(null=True, blank=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    country = models.ForeignKey('countries.country')
    state = models.ForeignKey('countries.state')
    verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Breeder"
        verbose_name_plural = "Breeders"

    def __unicode__(self):
        return u'%s %s' % (self.user.full_name, self.breeder_type)

    def save(
        self, force_insert=False, force_update=False, using=None,
        update_fields=None
    ):
        if self.country != self.state.country:
            raise ValueError("State missmatch country.")
        super(self, Breeder).save(
            force_insert, force_update, using, update_fields)


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
