from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render

from ella_flatcomments.models import CommentList, FlatComment
from ella_flatcomments.conf import comments_settings

def list_comments(request, context):
    # TODO: get reversed preferences from request
    clist = CommentList.for_object(context['object'])
    paginator = Paginator(clist, comments_settings.PAGINATE_BY)
    try:
        context['page'] = paginator.get_page(request.GET.get('p', 1))
        context['comment_list'] = context['page'].object_list
    except (PageNotAnInteger, EmptyPage):
        raise Http404()

    return render(request, )

def post_comment(request, context, comment_id=None):
    pass

def comment_detail(request, context, comment_id):
    clist = CommentList.for_object(context['object'])
    try:
        comment = clist.get_comment(comment_id)
    except FlatComment.DoesNotExist:
        raise Http404()

    # avoid additional lookup
    comment.content_object = context['object']
    # TODO: get reversed preferences from request
    return HttpResponseRedirect(comment.get_absolute_url())

def moderate_comment(request, context, comment_id):
    clist = CommentList.for_object(context['object'])
    try:
        comment = clist.get_comment(comment_id)
    except FlatComment.DoesNotExist:
        raise Http404()

    FlatComment.models.moderate_comment(comment, request.user)
    return HttpResponse('{"error": false}')
