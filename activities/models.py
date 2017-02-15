from __future__ import unicode_literals

from django.db import models


class Activity(models.Model):
    COMMENT = 'comment'
    LIKE = 'like'
    UPVOTE = 'upvote'
    FOLLOW = 'follow'

    ACTIVITY_CHOICES = (
        (COMMENT, 'New Comment.'),
        (LIKE, 'New Like.'),
        (UPVOTE, 'New Upvote.'),
        (FOLLOW, 'New User follow.')
    )

    user = models.ForeignKey('users.User', related_name='activities')
    action = models.CharField(choices=ACTIVITY_CHOICES, max_length=50)
    post = models.ForeignKey('posts.post', null=True, blank=True)
    comment = models.ForeignKey('comments.comment', null=True, blank=True)
    follows = models.ForeignKey('users.user', null=True, blank=True)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Activity"
        verbose_name_plural = "Activities"

    def __unicode__(self):
        return u'user: %s //action: %s' % (
            self.user.username, self.get_action_display()
        )

    def save(self, *args, **kwargs):
        if self.action == self.COMMENT:
            if not self.post:
                raise ValueError(
                    "A post is needed."
                )
            if not self.comment:
                raise ValueError(
                    'A comment is needed.'
                )
        elif self.action == self.LIKE:
            if not self.post:
                raise ValueError(
                    "A post is needed."
                )
        elif self.action == self.UPVOTE:
            if not self.comment:
                raise ValueError(
                    "A comment is needed."
                )
        elif self.action == self.FOLLOW:
            if not self.follows:
                raise ValueError(
                    "The user followed is needed."
                )
        super(Activity, self).save(*args, **kwargs)
