from django import template
from django.contrib.auth.models import User

from test_ella_flatcomments.cases import CommentTestCase

from nose import tools

class TestFilters(CommentTestCase):
    MOD_TEMPLATE = template.Template('{% load comment_tags %}{% if user|can_moderate %}YES{% else %}NO{% endif %}')
    EDIT_TEMPLATE = template.Template('{% load comment_tags %}{% if user|can_edit:comment %}YES{% else %}NO{% endif %}')

    def test_staff_user_can_moderate(self):
        self.user.is_staff = True
        tools.assert_equals('YES', self.MOD_TEMPLATE.render(template.Context({'user': self.user})))

    def test_normal_user_cannot_moderate(self):
        tools.assert_equals('NO', self.MOD_TEMPLATE.render(template.Context({'user': self.user})))

    def test_staff_user_can_edit_comments(self):
        c = self._get_comment()
        tools.assert_equals('YES', self.EDIT_TEMPLATE.render(template.Context({'user': User(is_staff=True), 'comment': c})))

    def test_user_can_edit_their_comments(self):
        c = self._get_comment()
        tools.assert_equals('YES', self.EDIT_TEMPLATE.render(template.Context({'user': self.user, 'comment': c})))

    def test_user_cannot_edit_other_comments(self):
        c = self._get_comment()
        tools.assert_equals('NO', self.EDIT_TEMPLATE.render(template.Context({'user': User(username='not him', pk=12), 'comment': c})))
