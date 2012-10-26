from redis import StrictRedis

from django.test import TestCase
from django.conf import settings

class RedisTestCase(TestCase):
    def setUp(self):
        super(RedisTestCase, self).setUp()
        self.redis = StrictRedis(**settings.REDIS)

    def tearDown(self):
        super(RedisTestCase, self).tearDown()
        self.redis.flushdb()
