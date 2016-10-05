from __future__ import unicode_literals
from django.db import models
from django.utils.timezone import now

PET_GENDER = (
    ('male', 'Male'),
    ('female', 'Female')
)
PET_TYPE = (
    ('dog', 'Dog'),
    ('cat', 'Cat'),
    ('other', 'Other')
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


class PetType(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Pet Type"
        verbose_name_plural = "Pet Types"

    def __unicode__(self):
        return u'%s' % (self.name)


class Pet(models.Model):
    name = models.CharField(max_length=50)
    fixed = models.BooleanField(default=False)
    image = models.ImageField(null=True, blank=True, upload_to=uploads_path)
    birth_year = models.IntegerField()  # We just need the year
    pet_type = models.ForeignKey(PetType)
    breed = models.CharField(max_length=150, null=True, blank=True)
    gender = models.CharField(choices=PET_GENDER, max_length=50)
    user = models.ForeignKey('users.User')  # 20 limit per user

    class Meta:
        verbose_name = "Pet"
        verbose_name_plural = "Pets"

    def __unicode__(self):
        return u"%s - %s" % (self.id, self.name)

    def age_verify(self):
        if self.birth_year > get_current_year():
            raise ValueError(
                'The pet year of birth cannot be higher than the current year')
        if self.birth_year < get_limit_year():
            raise ValueError(
                'The pet year of birth cannot be ' +
                'lower than' + str(get_limit_year()))

    def save(self, *args, **kwargs):
        self.age_verify()

        return super(Pet, self).save(*args, **kwargs)
