from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from django.conf.urls.defaults import patterns, url

from ella_flatcomments.views import list_comments, post_comment, comment_detail, moderate_comment, lock_comments, unlock_comments

urlpatterns = patterns('',
    url(r'^$', list_comments, name='comments-list'),
    url(r'^%s/$' % slugify(_('new')), post_comment, name='comment-new'),
    url(r'^(?P<comment_id>\d+)/$', comment_detail, name='comment-detail'),
    url(r'^(?P<comment_id>\d+)/%s/$' % slugify(_('update')), post_comment, name='comment-update'),
    url(r'^(?P<comment_id>\d+)/%s/$' % slugify(_('moderate')), moderate_comment, name='comment-moderate'),

    url(r'^%s/$' % slugify(_('lock')), lock_comments, name='comments-lock'),
    url(r'^%s/$' % slugify(_('unlock')), unlock_comments, name='comments-unlock'),
)

