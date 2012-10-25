from redis import Redis

from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from app_data import AppDataField

from ella.core.cache.fields import ContentTypeForeignKey, CachedGenericForeignKey, SiteForeignKey, CachedForeignKey
from ella.core.cache import get_cached_objects, get_cached_object, SKIP

from ella_flatcomments.signals import comment_was_moderated, comment_will_be_posted, comment_was_posted
from ella_flatcomments.conf import comments_settings

class CommentList(object):
    def __init__(self, content_type, object_id, reversed=False):
        self._key = comments_settings.LIST_KEY % (Site.objects.get_current().id, content_type.id, object_id)
        self._redis = Redis(**comments_settings.REDIS)
        self._reversed = reversed

    def count(self):
        return self._redis.llen(self._key)
    __len__ = count

    def __getitem__(self, key):
        if isinstance(key, int):
            return get_cached_object(Comment, pk=self._redis.lindex(self._key, key))

        assert isinstance(key, slice) and isinstance(key.start, int) and isinstance(key.stop, int) and key.step is None

        return get_cached_objects(self._redis.lrange(self._key, key.start, key.stop - 1), model=Comment, missing=SKIP)

    def add_comment(self, comment):
        self._redis.lpush(self._key, comment.id)

    def remove_comment(self, comment):
        self._redis.lrem(self._key, 0, comment.id)

class CommentManager(models.Manager):
    def post_comment(self, comment, request):
        """
        Post comment, fire of all the signals connected to that event and see
        if any receiver shut the posting down.

        Return error boolean and reason for error, if any.
        """
        responses = comment_will_be_posted(self.model, comment=comment, request=request)
        for (receiver, response) in responses:
            if response == False:
                return False, "comment_will_be_posted receiver %r killed the comment" % receiver.__name__
        comment.save(force_insert=True)
        responses = comment_was_posted(self.model, comment=comment, request=request)
        return True, None

    def moderate_comment(self, comment, user):
        """
        Mark some comment as moderated and fire a signal to make other apps aware of this
        """
        if not comment.is_public:
            return
        comment.is_public = False
        self.filter(pk=comment.pk).update(is_public=False)
        comment_was_moderated.send(self.model, comment=comment, user=user)


class Comment(models.Model):
    site = SiteForeignKey(default=Site.objects.get_current)

    content_type = ContentTypeForeignKey()
    object_id = models.IntegerField()
    content_object = CachedGenericForeignKey('content_type', 'object_id')

    content = models.TextField()

    submit_date = models.DateTimeField()
    user = CachedForeignKey(User)
    is_public = models.BooleanField(default=True)

    app_data = AppDataField()

    objects = CommentManager()

