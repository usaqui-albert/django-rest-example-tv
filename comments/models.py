from django.db import models


class Comment(models.Model):
    description = models.CharField(max_length=1200)

    user = models.ForeignKey('users.User', related_name='comments')
    post = models.ForeignKey('posts.Post', related_name='comments')
    upvoters = models.ManyToManyField(
        'users.User', related_name='upvotes', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'comment: %s - created: %s' % (self.id, self.created_at)


class Feedback(models.Model):
    comment = models.ForeignKey(Comment)
    user = models.ForeignKey('users.user')
    was_helpful = models.BooleanField()
    description = models.CharField(max_length=500, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.comment.post.user == self.user:
            raise ValueError(
                "Error: The user has to be the same that the post owner"
            )
        super(Feedback, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'FEEDBACK: user:%s, post: %s' % (
            self.user.id, self.comment.post.id)
