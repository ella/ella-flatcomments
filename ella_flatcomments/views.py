from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.template.response import TemplateResponse

from ella.core.views import get_templates_from_publishable
from ella.utils.timezone import now

from ella_flatcomments.models import CommentList, FlatComment
from ella_flatcomments.conf import comments_settings
from ella_flatcomments.forms import FlatCommentMultiForm
from ella_flatcomments.utils import show_reversed
from ella_flatcomments.signals import comment_updated

mod_required = user_passes_test(comments_settings.IS_MODERATOR_FUNC)

def get_template(name, obj=None, async=False):
    if async:
        name = '%s_async.%s' % tuple(name.rsplit('.', 1))
    if hasattr(obj, 'get_templates'):
        return obj.get_templates(name)
    return get_templates_from_publishable(name, obj)

def list_comments(request, context, reverse=None):
    if reverse is None:
        reverse = show_reversed(request)
    clist = CommentList.for_object(context['object'], reverse)
    paginator = Paginator(clist, comments_settings.PAGINATE_BY)
    try:
        p = request.GET.get('p', 1)
        if p == 'last':
            context['page'] = paginator.page(paginator.num_pages)
        else:
            context['page'] = paginator.page(p)
    except (PageNotAnInteger, EmptyPage):
        raise Http404()

    context['comment_list'] = context['page'].object_list
    context['is_paginated'] = context['page'].has_other_pages()
    return TemplateResponse(request, get_template('comment_list.html', context['object'], request.is_ajax()), context)

def comment_detail(request, context, comment_id):
    clist = CommentList.for_object(context['object'])
    try:
        comment = clist.get_comment(comment_id)
    except FlatComment.DoesNotExist:
        raise Http404()

    # avoid additional lookup
    comment.content_object = context['object']
    return HttpResponseRedirect(comment.get_absolute_url(show_reversed(request)))

@login_required
def post_comment(request, context, comment_id=None):
    clist = CommentList.for_object(context['object'])

    if clist.locked():
        return TemplateResponse(request, get_template('comments_locked.html', context['object'], request.is_ajax()), context, status=403)

    comment = None
    user = request.user
    if comment_id:
        try:
            comment = clist.get_comment(comment_id)
        except FlatComment.DoesNotExist:
            raise Http404()

        # make sure we don't change user when mod is editting a comment
        user = comment.user

        # you can only comment your own comments or you have to be a moderator
        if comment.user != request.user and not comments_settings.IS_MODERATOR_FUNC(request.user):
            return HttpResponseForbidden("You cannot edit other people's comments.")

    data, files = None, None
    if request.method == 'POST':
        data, files = request.POST, request.FILES

    form = FlatCommentMultiForm(context['object'], user, data=data, files=files, instance=comment)
    if form.is_valid():
        comment, success, reason = form.post(request)
        if not success:
            return HttpResponseForbidden(reason)
        comment_updated.send(
            sender=comment.__class__,
            comment=comment,
            updating_user=request.user,
            date_updated=now()
        )

        if request.is_ajax():
            context.update({'comment': comment})
            return TemplateResponse(request, get_template('comment_detail_async.html', context['object']), context)
        return HttpResponseRedirect(comment.get_absolute_url(show_reversed(request)))

    context.update({
        'comment': comment,
        'form': form
    })
    return TemplateResponse(request, get_template('comment_form.html', context['object'], request.is_ajax()), context)

@mod_required
@require_POST
def moderate_comment(request, context, comment_id):
    clist = CommentList.for_object(context['object'])
    try:
        comment = clist.get_comment(comment_id)
    except FlatComment.DoesNotExist:
        raise Http404()

    url = comment.get_absolute_url()
    comment.moderate(request.user)
    if request.is_ajax():
        return HttpResponse('{"error": false}', content_type='application/json')
    return HttpResponseRedirect(url)

@mod_required
@require_POST
def lock_comments(request, context):
    clist = CommentList.for_object(context['object'])
    clist.lock()
    if request.is_ajax():
        return HttpResponse('{"error": false}', content_type='application/json')
    return HttpResponseRedirect(context['object'].get_absolute_url())

@mod_required
@require_POST
def unlock_comments(request, context):
    clist = CommentList.for_object(context['object'])
    clist.unlock()
    if request.is_ajax():
        return HttpResponse('{"error": false}', content_type='application/json')
    return HttpResponseRedirect(context['object'].get_absolute_url())
