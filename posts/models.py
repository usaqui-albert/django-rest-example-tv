from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from pets.models import uploads_path


class Post(models.Model):
    description = models.CharField(max_length=1200)
    visible_by_vet = models.BooleanField(default=False)
    visible_by_owner = models.BooleanField(default=True)

    pet = models.ForeignKey('pets.Pet', related_name='posts', null=True)
    user = models.ForeignKey('users.User', related_name='posts')
    likers = models.ManyToManyField(
        'users.User', related_name='likes', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'Post %s - created at: %s' % (self.id, self.created_at)

    def set_paid(self):
        self.visible_by_vet = True
        self.visible_by_owner = True
        return self

    def is_paid(self):
        return self.visible_by_owner and self.visible_by_vet

    def get_likes(self):
        return self.likers.count()

    def save(self, *args, **kwargs):
        if self.user.is_vet():
            try:
                self.visible_by_vet = True and self.user.veterinarian.verified
            except ObjectDoesNotExist:
                self.visible_by_vet = False
            self.visible_by_owner = False
        super(Post, self).save(*args, **kwargs)


class ImagePost(models.Model):
    post = models.ForeignKey(Post, related_name='images')
    standard = models.ImageField(upload_to=uploads_path)
    thumbnail = models.ImageField(upload_to=uploads_path)
