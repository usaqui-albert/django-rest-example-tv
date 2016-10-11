from django.db import models


class Comment(models.Model):
    upvotes = models.PositiveIntegerField(default=0)
    description = models.CharField(max_length=1200)

    user = models.ForeignKey('users.User', related_name='comments')
    post = models.ForeignKey('posts.Post', related_name='comments')
    upvoters = models.ManyToManyField('users.User', related_name='upvotes')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'cooment:%s - created: %s' % (self.id, self.created_at)
