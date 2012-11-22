from django.contrib.contenttypes.models import ContentType

from ella.core.cache.utils import SKIP

from ella_flatcomments.models import FlatComment, CommentList

from test_ella_flatcomments.cases import CommentTestCase, PublishableTestCase

from nose import tools
from mock import patch, DEFAULT

class TestURL(PublishableTestCase):
    def test_first_comment_points_to_first_page(self):
        c = self._get_comment()
        self.comment_list.post_comment(c, None)

        tools.assert_equals(self.publishable.get_absolute_url() + 'comments/?p=1', c.get_absolute_url())

    def test_third_comment_on_second_page(self):
        comments = [self._get_comment() for _ in range(3)]
        for c in comments:
            self.comment_list.post_comment(c, None)

        tools.assert_equals(self.publishable.get_absolute_url() + 'comments/?p=2', comments[0].get_absolute_url())
        tools.assert_equals(self.publishable.get_absolute_url() + 'comments/?p=1', comments[1].get_absolute_url())

class TestRedisDenormalizations(CommentTestCase):
    def test_comment_id_is_pushed_to_redis_list(self):
        c = self._get_comment()
        self.comment_list.post_comment(c, None)

        tools.assert_equals(['comments:1:%s:1' % self.content_type.pk], self.redis.keys('*'))
        tools.assert_equals([str(c.pk)], self.redis.lrange('comments:1:%s:1' % self.content_type.pk, 0, -1))

    def test_moderate_removes_comment_id_from_redis(self):
        c = self._get_comment()
        c.save()
        self.redis.lpush('comments:1:%s:1' % self.content_type.pk, c.pk)

        self.comment_list.moderate_comment(c, self.user)
        tools.assert_equals([], self.redis.keys('*'))

    def test_delete_removes_comment_id_from_redis(self):
        c = self._get_comment()
        c.save()
        self.redis.lpush('comments:1:%s:1' % self.content_type.pk, c.pk)
        c.delete()

        tools.assert_equals([], self.redis.keys('*'))

class TestCommentManager(CommentTestCase):
    def test_get_comment_raises_does_not_exist_on_mismatched_content_object(self):
        c = self._get_comment()
        self.comment_list.post_comment(c, None)

        clist = CommentList.for_object(ContentType.objects.get(pk=2))
        tools.assert_raises(FlatComment.DoesNotExist, clist.get_comment, c.pk)

    def test_get_comment_works(self):
        c = self._get_comment()
        self.comment_list.post_comment(c, None)

        clist = CommentList.for_object(self.content_object)
        tools.assert_equals(c, clist.get_comment(c.pk))

class TestCommentList(CommentTestCase):
    def _patch(self, path, new=DEFAULT):
        patcher = patch(path, new)
        mocked = patcher.start()
        self.addCleanup(patcher.stop)
        return mocked


    def _get_cached_object(self, model, pk):
        tools.assert_equals(FlatComment, model)
        return int(pk)

    def _get_cached_objects(self, pks, model, missing):
        tools.assert_equals(FlatComment, model)
        tools.assert_equals(SKIP, missing)
        return map(int, pks)

    def setUp(self):
        super(TestCommentList, self).setUp()
        self.key = 'comments:1:%s:1' % self.content_type.pk
        for x in xrange(11):
            self.redis.lpush(self.key, x)

        self.get_cached_object = self._patch('ella_flatcomments.models.get_cached_object', self._get_cached_object)
        self.get_cached_objects = self._patch('ella_flatcomments.models.get_cached_objects', self._get_cached_objects)

    def test_len(self):
        tools.assert_equals(11, self.comment_list.count())
        tools.assert_equals(11, len(self.comment_list))

    def test_getitem(self):
        for i, c in zip(xrange(11), reversed(xrange(11))):
            tools.assert_equals(c, self.comment_list[i])

    def test_reversed_getitem(self):
        comment_list = CommentList(self.content_type, 1, reversed=True)
        for i, c in zip(xrange(11), xrange(11)):
            tools.assert_equals(c, comment_list[i])

    def test_last_comment_returns_none_on_no_comment(self):
        self.redis.delete(self.key)
        tools.assert_equals(None, self.comment_list.last_comment())

    def test_get_last_comment(self):
        tools.assert_equals(10, self.comment_list.last_comment())

    def test_get_last_comment_on_reversed_list(self):
        self.comment_list._reversed = True
        tools.assert_equals(10, self.comment_list.last_comment())

    def test_slice(self):
        clist = range(11)
        clist.reverse()
        tools.assert_equals(clist[0:4], self.comment_list[0:4])
        tools.assert_equals(clist[2:6], self.comment_list[2:6])
        tools.assert_equals(clist[2:60], self.comment_list[2:60])

    def test_reversed_slice(self):
        comment_list = CommentList(self.content_type, 1, reversed=True)
        clist = range(11)
        tools.assert_equals(clist[0:4], comment_list[0:4])
        tools.assert_equals(clist[2:6], comment_list[2:6])
        tools.assert_equals(clist[2:60], comment_list[2:60])

