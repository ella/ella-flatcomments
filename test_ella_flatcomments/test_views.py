from django.test import RequestFactory
from django.http import Http404
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User

from ella_flatcomments import views
from ella_flatcomments.signals import comment_was_posted

from nose import tools

from test_ella_flatcomments.cases import PublishableTestCase

class ViewTestCase(PublishableTestCase):
    def setUp(self):
        super(ViewTestCase, self).setUp()
        self.rf = RequestFactory()
        self.superuser = User.objects.create_superuser('superuser', 'user@example.com', '!')

    def get_request(self, method='GET', path='/', user=AnonymousUser(), data={}):
        request = getattr(self.rf, method.lower())(path, data)
        request.user = user
        return request

    def get_context(self, **kwargs):
        defaults = {
            'object': self.publishable,
            'category': self.category_nested,
        }
        defaults.update(kwargs)
        return defaults

class TestCommentList(ViewTestCase):
    def test_empty_list_returned_with_no_comments(self):
        response = views.list_comments(self.get_request(), self.get_context())

        tools.assert_equals([], response.context_data['comment_list'])

    def test_raises_404_on_empty_page(self):
        tools.assert_raises(Http404, views.list_comments, self.get_request(data={'p': '2'}), self.get_context())

    def test_raises_404_on_invalid_page(self):
        tools.assert_raises(Http404, views.list_comments, self.get_request(data={'p': 'not a number'}), self.get_context())

    def test_displays_last_page_on_request(self):
        response = views.list_comments(self.get_request(data={'p': 'last'}), self.get_context())

        tools.assert_equals([], response.context_data['comment_list'])

class TestComment_detail(ViewTestCase):
    def test_raises_404_on_missing_comment(self):
        tools.assert_raises(Http404, views.comment_detail, self.get_request(), self.get_context(), 1)

    def test_redirects_to_comment_url(self):
        c = self._get_comment()
        c.post()

        response = views.comment_detail(self.get_request(), self.get_context(), str(c.pk))

        tools.assert_equals(302, response.status_code)
        tools.assert_equals(c.get_absolute_url(), response['Location'])

class TestPostComment(ViewTestCase):
    def setUp(self):
        super(TestPostComment, self).setUp()
        comment_was_posted.connect(self._comment_posted)
        self._posted = []

    def tearDown(self):
        super(TestPostComment, self).tearDown()
        comment_was_posted.disconnect(self._comment_posted)

    def _comment_posted(self, *args, **kwargs):
        self._posted.append((args, kwargs))

    def test_login_required(self):
        response = views.post_comment(self.get_request(method='POST'), self.get_context())
        tools.assert_equals(302, response.status_code)

    def test_honeypot_causes_post_to_fail(self):
        response = views.post_comment(self.get_request(method='POST', user=self.user, data={'comment': 'New Comment!', 'honeypot': 'Heya'}), self.get_context())
        tools.assert_equals(200, response.status_code)
        tools.assert_equals(0, self.comment_list.count())

    def test_post_with_content_goes_through(self):
        req = self.get_request(method='POST', user=self.user, data={'comment': 'New Comment!'})
        response = views.post_comment(req, self.get_context())

        tools.assert_equals(302, response.status_code)
        tools.assert_equals(1, self.comment_list.count())
        c = self.comment_list.last_comment()
        tools.assert_equals(c.get_absolute_url(), response['Location'])
        tools.assert_equals(c.comment, 'New Comment!')
        tools.assert_equals(1, len(self._posted))
        
        args, kwargs = self._posted[0]
        tools.assert_equals(req, kwargs['request'])


    def test_users_can_edit_their_comments(self):
        c = self._get_comment()
        c.post()
        response = views.post_comment(self.get_request(method='POST', user=self.user, data={'comment': 'New Comment Text!'}), self.get_context(), str(c.pk))

        tools.assert_equals(302, response.status_code)
        tools.assert_equals(1, self.comment_list.count())
        c = self.comment_list.last_comment()
        tools.assert_equals(c.get_absolute_url(), response['Location'])
        tools.assert_equals(c.comment, 'New Comment Text!')

    def test_users_cannot_other_users_comments(self):
        c = self._get_comment()
        c.post()
        user = User.objects.create_user('some_OTHER_user', 'user@example.com')

        response = views.post_comment(self.get_request(method='POST', user=user, data={'comment': 'New Comment Text!'}), self.get_context(), str(c.pk))

        tools.assert_equals(403, response.status_code)
        c = self.comment_list.last_comment()
        tools.assert_not_equals(c.comment, 'New Comment Text!')

    def test_staff_can_edit_other_users_comments(self):
        c = self._get_comment()
        c.post()
        response = views.post_comment(self.get_request(method='POST', user=self.superuser, data={'comment': 'New Comment Text!'}), self.get_context(), str(c.pk))

        tools.assert_equals(302, response.status_code)
        tools.assert_equals(1, self.comment_list.count())
        c = self.comment_list.last_comment()
        tools.assert_equals(c.get_absolute_url(), response['Location'])
        tools.assert_equals(c.comment, 'New Comment Text!')
        tools.assert_equals(self.user, c.user)


class TestLockUnLockComments(ViewTestCase):
    def test_login_required_for_lock(self):
        response = views.lock_comments(self.get_request(method='POST'), self.get_context())
        tools.assert_equals(302, response.status_code)
        tools.assert_false(self.comment_list.locked())

    def test_moderator_required_for_lock(self):
        response = views.lock_comments(self.get_request(method='POST', user=self.user), self.get_context())
        tools.assert_equals(302, response.status_code)
        tools.assert_false(self.comment_list.locked())

    def test_login_required_for_unlock(self):
        self.comment_list.lock()
        response = views.unlock_comments(self.get_request(method='POST'), self.get_context())
        tools.assert_equals(302, response.status_code)
        tools.assert_true(self.comment_list.locked())

    def test_moderator_required_for_unlock(self):
        self.comment_list.lock()
        response = views.unlock_comments(self.get_request(method='POST', user=self.user), self.get_context())
        tools.assert_equals(302, response.status_code)
        tools.assert_true(self.comment_list.locked())

    def test_lock_locks(self):
        response = views.lock_comments(self.get_request(method='POST', user=self.superuser), self.get_context())
        tools.assert_equals(302, response.status_code)
        tools.assert_true(self.comment_list.locked())

    def test_unlock_unlocks(self):
        self.comment_list.lock()
        response = views.unlock_comments(self.get_request(method='POST', user=self.superuser), self.get_context())
        tools.assert_equals(302, response.status_code)
        tools.assert_false(self.comment_list.locked())


class TestModerateComment(ViewTestCase):
    def setUp(self):
        super(TestModerateComment, self).setUp()
        self.comment = self._get_comment()
        self.comment.post()

    def test_login_required(self):
        response = views.moderate_comment(self.get_request(method='POST'), self.get_context(), self.comment.pk)
        tools.assert_equals(302, response.status_code)
        tools.assert_equals(1, self.comment_list.count())

    def test_moderator_required(self):
        response = views.moderate_comment(self.get_request(method='POST', user=self.user), self.get_context(), self.comment.pk)
        tools.assert_equals(302, response.status_code)
        tools.assert_equals(1, self.comment_list.count())

    def test_post_required(self):
        response = views.moderate_comment(self.get_request(method='GET', user=self.superuser), self.get_context(), self.comment.pk)
        tools.assert_equals(405, response.status_code)
        tools.assert_equals(1, self.comment_list.count())

    def test_moderated(self):
        response = views.moderate_comment(self.get_request(method='POST', user=self.superuser), self.get_context(), self.comment.pk)

        tools.assert_equals(302, response.status_code)
        tools.assert_equals(0, self.comment_list.count())
