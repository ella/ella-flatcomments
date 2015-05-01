from ella_flatcomments.forms import FlatCommentMultiForm
from ella_flatcomments.signals import comment_was_posted

from nose import tools

from test_ella_flatcomments.cases import CommentTestCase

class TestForm(CommentTestCase):
    def setUp(self):
        super(TestForm, self).setUp()
        comment_was_posted.connect(self._comment_posted)
        self._posted = []

    def tearDown(self):
        super(TestForm, self).tearDown()
        comment_was_posted.disconnect(self._comment_posted)

    def _comment_posted(self, *args, **kwargs):
        self._posted.append((args, kwargs))

    def test_request_is_passed_through_on_post(self):
        request = object()
        form = FlatCommentMultiForm(self.content_object, self.user, data={'comment': 'Works!'})
        form.post(request)

        tools.assert_equals(1, len(self._posted))
        tools.assert_is(request, self._posted[0][1]['request'])
        

