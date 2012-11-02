from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.template.response import TemplateResponse

from ella.core.views import get_templates_from_publishable

from ella_flatcomments.models import CommentList, FlatComment
from ella_flatcomments.conf import comments_settings
from ella_flatcomments.forms import FlatCommentMultiForm

mod_required = user_passes_test(comments_settings.IS_MODERATOR_FUNC)

def get_template(name, obj=None):
    if hasattr(obj, 'get_templates'):
        return obj.get_templates(name)
    return get_templates_from_publishable(name, obj)

def show_reversed(request):
    # TODO: get reversed preferences from request
    # TODO: maybe also pass in the object to makethe decision
    return False

def list_comments(request, context):
    clist = CommentList.for_object(context['object'], show_reversed(request))
    paginator = Paginator(clist, comments_settings.PAGINATE_BY)
    try:
        context['page'] = paginator.page(request.GET.get('p', 1))
    except (PageNotAnInteger, EmptyPage):
        raise Http404()

    context['comment_list'] = context['page'].object_list
    return TemplateResponse(request, get_template('comment_list.html', context['object']), context)

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
@require_POST
def post_comment(request, context, comment_id=None):
    clist = CommentList.for_object(context['object'])
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

    form = FlatCommentMultiForm(context['object'], user, data=request.POST, files=request.FILES, instance=comment)
    if form.is_valid():
        comment = form.save(commit=False)
        success, reason = clist.post_comment(comment, request)
        if not success:
            return HttpResponseForbidden(reason)
        return HttpResponseRedirect(comment.get_absolute_url(show_reversed(request)))

    context.update({
        'comment': comment,
        'form': form
    })
    return TemplateResponse(request, get_template('comment_form.html', context['object']), context)

@mod_required
@require_POST
def moderate_comment(request, context, comment_id):
    clist = CommentList.for_object(context['object'])
    try:
        comment = clist.get_comment(comment_id)
    except FlatComment.DoesNotExist:
        raise Http404()

    url = comment.get_absolute_url()
    clist.moderate_comment(comment, request.user)
    if request.is_ajax():
        return HttpResponse('{"error": false}', content_type='application/json')
    return HttpResponseRedirect(url)
