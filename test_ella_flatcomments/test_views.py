from django.test import RequestFactory
from django.http import Http404
from django.contrib.auth.models import AnonymousUser

from ella_flatcomments import views

from nose import tools

from test_ella_flatcomments.cases import PublishableTestCase

class ViewTestCase(PublishableTestCase):
    def setUp(self):
        super(ViewTestCase, self).setUp()
        self.rf = RequestFactory()

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

    def test_throws_404_on_empty_page(self):
        tools.assert_raises(Http404, views.list_comments, self.get_request(data={'p': '2'}), self.get_context())

    def test_throws_404_on_invalid_page(self):
        tools.assert_raises(Http404, views.list_comments, self.get_request(data={'p': 'not a number'}), self.get_context())
