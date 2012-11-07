from django import template
from django.contrib.auth.models import User

from ella_flatcomments.templatetags.comment_tags import CommentFormNode, CommentCountNode, CommentListNode, _parse_comment_tag
from ella_flatcomments.models import CommentList
from ella_flatcomments.forms import FlatCommentMultiForm
from ella_flatcomments.conf import comments_settings

from test_ella_flatcomments.cases import CommentTestCase

from nose import tools

from mock import patch

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

class TestCommentForm(CommentTestCase):
    def test_syntax_error_on_wrong_syntax(self):
        tools.assert_raises(template.TemplateSyntaxError, template.Template, '{% load comment_tags %}{% comment_form for XXX as YYY additional_stuff %}')
        tools.assert_raises(template.TemplateSyntaxError, template.Template, '{% load comment_tags %}{% comment_form for XXX as %}')
        tools.assert_raises(template.TemplateSyntaxError, template.Template, '{% load comment_tags %}{% comment_form for XXX = YYY %}')
        tools.assert_raises(template.TemplateSyntaxError, template.Template, '{% load comment_tags %}{% comment_form from XXX as YYY %}')

    def test_correct_form_is_set_in_context(self):
        cfn = CommentFormNode(template.Variable('object'), 'form')
        c = template.Context({'user': self.user, 'object': self.content_object})

        cfn.render(c)
        tools.assert_true('form' in c)
        form = c['form']
        tools.assert_true(isinstance(form, FlatCommentMultiForm))
        tools.assert_equals(self.content_object, form.model_form.content_object)
        tools.assert_equals(self.user, form.model_form.user)

class TestCommentNodeParsing(CommentTestCase):
    '''
    {% comment_tag for object as var %}
    {% comment_tag for content_type object_id as var %}
    '''
    def setUp(self):
        super(TestCommentNodeParsing, self).setUp()
        self.context = template.Context({'request': None, 'user': self.user, 'object': self.content_object, 'ct': self.content_type, 'obj_pk': 1})

    def test_value_from_var(self):
        ccnode = _parse_comment_tag(['comment_list', 'for', 'object', 'as', 'var'], CommentCountNode)

        tools.assert_true(isinstance(ccnode, CommentCountNode))
        comment_list = ccnode.get_comment_list(self.context)

        tools.assert_equals(self.content_type.pk, comment_list.ct_id)
        tools.assert_equals('1', comment_list.obj_id)

    def test_value_from_ct_id_pair(self):
        ccnode = _parse_comment_tag(['comment_list', 'for', 'ct', 'obj_pk', 'as', 'var'], CommentListNode)

        tools.assert_true(isinstance(ccnode, CommentListNode))
        comment_list = ccnode.get_comment_list(self.context)

        tools.assert_equals(self.content_type.pk, comment_list.ct_id)
        tools.assert_equals('1', comment_list.obj_id)

    def test_comment_count(self):
        t = template.Template('{% load comment_tags %}{% comment_count for object as cnt %}{{ cnt }}')
        class MyCommentList(CommentList):
            def count(self):
                return 42
        patcher = patch('ella_flatcomments.templatetags.comment_tags.CommentList', MyCommentList)
        patcher.start()
        self.addCleanup(patcher.stop)

        tools.assert_equals('42', t.render(self.context))

    def test_comment_list(self):
        t = template.Template('{% load comment_tags %}{% comment_list for object as clist %}{{ clist }}')
        class MyCommentList(CommentList):
            def __getitem__(self, key):
                return '%s:%s' % (key.start, key.stop)

        patcher = patch('ella_flatcomments.templatetags.comment_tags.CommentList', MyCommentList)
        patcher.start()
        self.addCleanup(patcher.stop)

        tools.assert_equals('None:%d' % comments_settings.PAGINATE_BY, t.render(self.context))
