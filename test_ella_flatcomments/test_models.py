from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from ella_flatcomments.models import FlatComment, CommentList

from test_ella_flatcomments.cases import RedisTestCase

from nose import tools
from mock import patch, DEFAULT


class CommentTestCase(RedisTestCase):
    def setUp(self):
        super(CommentTestCase, self).setUp()
        self.content_object = ContentType.objects.get(pk=1)
        self.content_type = ContentType.objects.get_for_model(ContentType)
        self.user = User.objects.create_user('some_user')

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

class TestRedisDenormalizations(CommentTestCase):
    def test_comment_id_is_pushed_to_redis_list(self):
        c = self._get_comment()
        FlatComment.objects.post_comment(c, None)

        tools.assert_equals(['comments:1:%s:1' % self.content_type.pk], self.redis.keys('*'))
        tools.assert_equals([str(c.pk)], self.redis.lrange('comments:1:%s:1' % self.content_type.pk, 0, -1))

    def test_delete_removes_comment_id_from_redis(self):
        c = self._get_comment()
        c.save()
        self.redis.lpush('comments:1:%s:1' % self.content_type.pk, c.pk)

        FlatComment.objects.moderate_comment(c, self.user)
        tools.assert_equals([], self.redis.keys('*'))

class TestCommentList(CommentTestCase):
    def _patch(self, path, new=DEFAULT):
        patcher = patch(path, new)
        mocked = patcher.start()
        self.addCleanup(patcher.stop)
        return mocked

    def _fake_comments(self, count):
        for x in xrange(count):
            self.redis.lpush(self.key, x)

    def _get_cached_object(self, model, pk):
        tools.assert_equals(FlatComment, model)
        return int(pk)

    def _get_cached_objects(self, pks, model, **kwargs):
        tools.assert_equals(FlatComment, model)
        return map(int, pks)

    def setUp(self):
        super(TestCommentList, self).setUp()
        self.comment_list = CommentList(self.content_type, 1)
        self.key = 'comments:1:%s:1' % self.content_type.pk
        self._fake_comments(11)

        self.get_cached_object = self._patch('ella_flatcomments.models.get_cached_object', self._get_cached_object)
        self.get_cached_objects = self._patch('ella_flatcomments.models.get_cached_objects', self._get_cached_objects)

    def test_len(self):
        tools.assert_equals(11, self.comment_list.count())
        tools.assert_equals(11, len(self.comment_list))

    def test_getitem(self):
        for i, c in zip(xrange(11), reversed(xrange(11))):
            tools.assert_equals(c, self.comment_list[i])

    def test_get_last_comment(self):
        tools.assert_equals(10, self.comment_list.last_comment())

    def test_slice(self):
        clist = range(11)
        clist.reverse()
        tools.assert_equals(clist[0:4], self.comment_list[0:4])
        tools.assert_equals(clist[2:6], self.comment_list[2:6])
        tools.assert_equals(clist[2:60], self.comment_list[2:60])
