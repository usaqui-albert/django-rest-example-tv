from django.contrib.auth.models import AbstractUser
from django.db import models


VETERINARIAN_TYPES = (
    ('tech', 'Technician'),
    ('vet', 'Veterinarian'),
    ('student', 'Student')
)


class User(AbstractUser):
    full_name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.email


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
