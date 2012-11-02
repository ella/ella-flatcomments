from django import template
from django.contrib.contenttypes.models import ContentType

from ella_flatcomments.conf import comments_settings
from ella_flatcomments.forms import FlatCommentMultiForm
from ella_flatcomments.models import CommentList
from ella_flatcomments.utils import show_reversed

register = template.Library()



@register.filter
def can_moderate(user):
    " {{ user|can_moderate }} "
    return comments_settings.IS_MODERATOR_FUNC(user)

@register.filter
def can_edit(comment, user):
    " {{ user|can_edit:comment }} "
    return comments_settings.IS_MODERATOR_FUNC(user) or comment.user == user

class BaseCommentListNode(template.Node):
    def __init__(self, lookup, out_var, **kwargs):
        self.lookup = lookup
        self.out_var = out_var
        self.kwargs = kwargs

    def value_from_comment_list(self, comment_list, context):
        raise

    def get_comment_list(self, context):
        reversed = show_reversed(context['request'])
        if isinstance(self.lookup, template.Variable):
            return CommentList.for_object(self.lookup.resolve(context), reversed)

        ct, obj_pk = map(lambda v: v.resolve(context), self.lookup)
        if isinstance(ct, int):
            ct = ContentType.objects.get_for_id(ct)

        return CommentList(ct, obj_pk, reversed)

    def render(self, context):
        try:
            comment_list = self.get_comment_list(context)
        except (template.VariableDoesNotExist, ContentType.DoesNotExist):
            return ''

        context[self.out_var] = self.value_from_comment_list(comment_list, context)
        return ''


def CommentCountNode(BaseCommentListNode):
    def value_from_comment_list(self, comment_list, context):
        return comment_list.count()


def CommentListNode(BaseCommentListNode):
    def value_from_comment_list(self, comment_list, context):
        return comment_list[:comments_settings.PAGINATE_BY]


def _parse_comment_tag(bits, docstring):
    if len(bits) not in (5, 6) or bits[1] != 'for' or bits[-2] != 'as':
        raise template.TemplateSyntaxError('{%% %s for {<content_type> <pk>|<var>} as <var_name> %%}' % bits[0])

    if len(bits) == 5:
        lookup = template.Variable(bits[2])
    else:
        lookup = map(template.Variable, bits[2:4])

    return lookup, bits[-1]

@register.tag
def comment_count(parser, token):
    """
    {% comment_count for <blabla> as cnt %}
    {% comment_count for <content_type> <pk> as cnt %}
    """
    return CommentCountNode(*_parse_comment_tag(token.split_contents()))

@register.tag
def comment_list(parser, token):
    """
    {% comment_list for <blabla> as clist %}
    {% comment_list for <content_type> <pk> as clist %}
    """
    return CommentListNode(*_parse_comment_tag(token.split_contents()))

class CommentFormNode(template.Node):
    def __init__(self, obj_var, form_var):
        self.obj_var = obj_var
        self.form_var = form_var

    def render(self, context):
        try:
            content_object = self.obj_var.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        context[self.form_var] = FlatCommentMultiForm(instance=content_object, user=context['user'])
        return ''

@register.tag
def comment_form(parser, token):
    """ {% comment_form for blabla as clist %} """
    bits = token.split_contents()
    if len(bits) != 5 or bits[1] != 'for' or bits[3] != 'as':
        raise template.TemplateSyntaxError(comment_form.__doc__)

    return CommentFormNode(template.Variable(bits[2]), bits[4])
