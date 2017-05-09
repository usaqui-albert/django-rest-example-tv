from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_save, post_delete

from .signals import (
    post_reporting_signal, new_post_like_signal, inactive_post_like_signal
)

min_max_range = [
    MinValueValidator(0),
    MaxValueValidator(20)
]


def uploads_path(instance, filename):
    '''
    Function to organize the upload directory
    this way, every file is organized by username and management
    is a lot faster
    '''
    return '/'.join(['uploads', 'posts', filename])


class UserLikesPost(models.Model):
    user = models.ForeignKey('users.User', related_name='user_likes')
    post = models.ForeignKey('posts.Post', related_name='user_likes')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __unicode__(self):
        return u'User: %s likes Post_id: %s' % (
            self.user.username, self.post.id
        )


# Func to connect the signal on post save.
post_save.connect(
    new_post_like_signal,
    sender=UserLikesPost,
    dispatch_uid="users.models.userlikespost_post_save"
)
post_delete.connect(
    inactive_post_like_signal,
    sender=UserLikesPost,
    dispatch_uid="users.models.userlikespost_post_delete"
)


class Post(models.Model):
    description = models.CharField(max_length=1200)
    visible_by_vet = models.BooleanField(default=False)
    visible_by_owner = models.BooleanField(default=True)

    pet = models.ForeignKey(
        'pets.Pet', related_name='posts', null=True,
        on_delete=models.SET_NULL, blank=True)
    user = models.ForeignKey('users.User', related_name='posts')
    likers = models.ManyToManyField(
        'users.User',
        through=UserLikesPost,
        related_name='likes',
        blank=True
    )
    active = models.BooleanField(default=True)
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

    def get_images(self):
        return self.images.count()

    def save(self, *args, **kwargs):
        if self.pk is None:
            if self.user.is_vet():
                try:
                    self.visible_by_vet = self.user.veterinarian.verified
                except ObjectDoesNotExist:
                    self.visible_by_vet = False
                self.visible_by_owner = False
        super(Post, self).save(*args, **kwargs)


class ImagePost(models.Model):
    post = models.ForeignKey(Post, related_name='images')
    image_number = models.PositiveSmallIntegerField(
        choices=((1, 1), (2, 2), (3, 3)), default=1)
    standard = models.ImageField(upload_to=uploads_path)
    thumbnail = models.ImageField(upload_to=uploads_path)

    def __unicode__(self):
        return u'Post %s - created at: %s' % (
            self.post.id, self.post.created_at)


class PaymentAmount(models.Model):
    description = models.CharField(max_length=100)
    value = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedVariable(models.Model):
    is_vet = models.BooleanField(default=False)
    post_quantity = models.PositiveSmallIntegerField(
        validators=min_max_range
    )
    posts_user_has_liked = models.PositiveSmallIntegerField(
        validators=min_max_range
    )
    posts_user_has_comment = models.PositiveSmallIntegerField(
        validators=min_max_range
    )
    posts_user_follows = models.PositiveSmallIntegerField(
        validators=min_max_range
    )
    posts_by_user = models.PositiveSmallIntegerField(
        validators=min_max_range
    )
    new_posts = models.PositiveSmallIntegerField(
        validators=min_max_range
    )
    paid_posts = models.PositiveSmallIntegerField(
        validators=min_max_range,
        null=True,
        blank=True
    )


class ActivePost(models.Model):
    post = models.ForeignKey('posts.Post', related_name='active_post_weight')
    created_at = models.DateTimeField(auto_now_add=True)


class Report(models.Model):
    OFFENSIVE = 1
    RELEVANT = 2
    SPAM = 3
    REPORT_TYPE = (
        (OFFENSIVE, 'offensive'),
        (RELEVANT, 'not relevant'),
        (SPAM, 'spam'),
    )

    post = models.ForeignKey(Post, related_name='reports')
    user = models.ForeignKey('users.User', related_name='reports')
    type = models.PositiveSmallIntegerField(choices=REPORT_TYPE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post', 'type')

    def get_type_as_string(self):
        return [y for x, y in self.REPORT_TYPE if x == self.type][0]


# Func to connect the signal on post save.
post_save.connect(
    post_reporting_signal,
    sender=Report,
    dispatch_uid="posts.models.report_post_save"
)


class PostReceipt(models.Model):
    APPLE = 'apple'
    GOOGLE = 'google'
    STORE_CHOICES = (
        (APPLE, 'App Store.'),
        (GOOGLE, 'Play Store.'),
    )
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    post = models.ForeignKey('posts.post', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    # Apple
    transacction_id = models.CharField(max_length=200)  # will store orderId
    receipt = models.CharField(max_length=1200, null=True, blank=True)
    # Google
    developerPayload = models.CharField(null=True, blank=True, max_length=50)
    purchaseToken = models.CharField(null=True, blank=True, max_length=50)
    store = models.CharField(
        choices=STORE_CHOICES, max_length=50, blank=True, null=True
    )

    def save(self, *args, **kwargs):
        msg = 'Incorrect Object'
        if not self.receipt:
            if not self.purchaseToken and self.developerPayload:
                raise ValidationError(msg)
            else:
                self.store = self.GOOGLE
        else:
            if self.purchaseToken:
                raise ValidationError(msg)
            if self.developerPayload:
                raise ValidationError(msg)
            if not (self.purchaseToken or self.developerPayload):
                self.store = self.APPLE

        super(PostReceipt, self).save(*args, **kwargs)
