from redis import StrictRedis

from django.test import TestCase
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from ella.utils.test_helpers import create_basic_categories, create_and_place_a_publishable

from ella_flatcomments.models import FlatComment

class RedisTestCase(TestCase):
    def setUp(self):
        super(RedisTestCase, self).setUp()
        self.redis = StrictRedis(**settings.REDIS)

    def tearDown(self):
        super(RedisTestCase, self).tearDown()
        self.redis.flushdb()

class CommentTestCase(RedisTestCase):
    def setUp(self):
        super(CommentTestCase, self).setUp()
        self.content_object = ContentType.objects.get(pk=1)
        self.content_type = ContentType.objects.get_for_model(ContentType)
        self.user = User.objects.create_user('some_user', 'user@example.com')

    def _get_comment(self, commit=False, **kwargs):
        defaults = dict(
            content_type=self.content_type,
            object_id=self.content_object.pk,
            user=self.user,
            content=''
        )
        defaults.update(kwargs)

        c = FlatComment(**defaults)
        if commit:
            c.save()
        return c

class PublishableTestCase(CommentTestCase):
    def setUp(self):
        super(PublishableTestCase, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

    def _create_comment(self, commit=False, **kwargs):
        defaults = {
            'content_type': self.publishable.content_type,
            'object_id': self.publishable.pk
        }
        defaults.update(kwargs)
        return super(PublishableTestCase, self)._create_comment(commit=commit, **defaults)

