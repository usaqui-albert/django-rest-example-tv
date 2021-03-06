from uuid import uuid4

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db.models.signals import post_save, m2m_changed
from django.utils import timezone

from pets.models import get_current_year, get_limit_year, uploads_path

from .signals import (
    create_auth_token, vet_signal, follows_changed
)
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
    IS_VET = [3, 4, 5]
    IS_OWNER = [1, 2]
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    full_name = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    stripe_token = models.CharField(max_length=100, null=True, blank=True)
    add_paid_post = models.BooleanField(default=True)

    follows = models.ManyToManyField(
        'users.user', related_name="followed_by", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    blur_images = models.BooleanField(default=False)
    interested_notification = models.BooleanField(default=True)
    vet_reply_notification = models.BooleanField(default=True)
    comments_notification = models.BooleanField(default=True)
    comments_like_notification = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __unicode__(self):
        return u'%d %s' % (self.id, self.username)

    def __str__(self):
        return self.email

    def get_short_name(self):
        return self.full_name

    def is_vet(self):
        if hasattr(self, 'groups'):
            return self.groups.pk in self.IS_VET
        else:
            return False

    def is_vet_student(self):
        if hasattr(self, 'groups'):
            return self.groups.id == 4
        else:
            return False

    def get_label(self):
        return settings.APP_LABEL.get(self.get_group_id(), '')

    def get_token(self):
        return self.auth_token.key if self.auth_token else None

    def save(self, *args, **kwargs):
        if self.is_vet():
            self.blur_images = False

        super(User, self).save(*args, **kwargs)

    def get_group_id(self, *args, **kwargs):
        return self.groups.id if hasattr(self, 'groups') else None


# Func to connect the signal on post save.
post_save.connect(
    create_auth_token,
    sender=User,
    dispatch_uid="users.models.user_post_save"
)

m2m_changed.connect(
    follows_changed, sender=User.follows.through)


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
                "The state does not belong to the selected country.")
        super(Breeder, self).save(*args, **kwargs)


class Veterinarian(models.Model):
    area_interest = models.ManyToManyField(AreaInterest, blank=True)
    veterinary_school = models.CharField(max_length=50, null=True, blank=True)
    graduating_year = models.IntegerField(null=True, blank=True)
    verified = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    veterinarian_type = models.CharField(
        choices=VETERINARIAN_TYPES, max_length=50)
    license_number = models.CharField(max_length=150, null=True, blank=True)
    country = models.ForeignKey('countries.Country', blank=True, null=True)
    state = models.ForeignKey('countries.State', blank=True, null=True)

    class Meta:
        verbose_name = "Veterinarian"
        verbose_name_plural = "Veterinarians"

    def __unicode__(self):
        return u'%s %s' % (self.user.full_name, self.veterinarian_type)

    def save(self, *args, **kwargs):
        if (
            hasattr(self.user, 'groups') and
            int(self.veterinarian_type) != self.user.groups.id
        ):
            raise ValidationError(
                "Group error"
            )
        if self.veterinarian_type != '4':
            if self.country is None or self.state is None:
                raise ValidationError(
                    "Country and state are required"
                )
            if self.country != self.state.country:
                raise ValueError(
                    "The state does not belong to the selected country.")
        else:
            if not self.graduating_year:
                raise ValueError(
                    'Graduating year is needed'
                )
            if not self.veterinary_school:
                raise ValueError(
                    'Veterinarian School is needed'
                )
            if self.graduating_year < get_limit_year():
                raise ValueError(
                    'The graduating year cannot be lower than ' +
                    str(get_limit_year()))
            if self.graduating_year > get_current_year() + 20:
                raise ValueError(
                    'The graduating year cannot be higher than ' +
                    'the year ' + str(get_current_year() + 20))
        super(Veterinarian, self).save(*args, **kwargs)

    def change_status(self):
        if not int(self.veterinarian_type) == 4:
            if self.verified or self.locked:
                if self.locked and not self.verified:
                    self.verified = True
                    self.locked = False
                else:
                    self.verified = self.locked = True
            else:
                self.verified = False
                self.locked = True
            return self
        return self


# Func to connect the signal on post save.
post_save.connect(
    vet_signal,
    sender=Veterinarian,
    dispatch_uid="users.models.veterinarian_post_save"
)


class ProfileImage(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='image')
    standard = models.ImageField(upload_to=uploads_path)
    thumbnail = models.ImageField(upload_to=uploads_path)

    class Meta:
        verbose_name = "Profile Image"
        verbose_name_plural = "Profile Images"

    def __str__(self):
        return u'Profile pic for: %s' % self.user.username


class VerificationCode(models.Model):
    code = models.CharField(max_length=6)
    user = models.OneToOneField(User, related_name='verification_code')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.code = str(uuid4().get_hex().upper()[0:6])
        super(VerificationCode, self).save(*args, **kwargs)

    def has_expired(self):
        return self.created_at <= timezone.now() - timezone.timedelta(days=1)
