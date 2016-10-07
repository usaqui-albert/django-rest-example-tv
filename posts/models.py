from django.db import models


class Post(models.Model):
    likes = models.PositiveIntegerField(default=0)
    description = models.CharField(max_length=1200)
    visible_by_vet = models.BooleanField(default=False)
    visible_by_owner = models.BooleanField(default=True)

    pet = models.ForeignKey('pets.Pet', related_name='posts', null=True)
    user = models.ForeignKey('users.User', related_name='posts')
    likers = models.ManyToManyField('users.User', related_name='likes')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
