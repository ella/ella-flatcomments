from django.contrib import comments

from ella_flatcomments.models import FlatComment

def show_reversed(request):
    reverse = False
    # TODO: maybe also pass in the content_type to makethe decision
    if 'reverse' in request.GET:
        reverse = bool(request.GET['reverse'])
    return reverse

def disconnect_legacy_signals():
    " Disconnect signals for ell-comments to allow tests and migrations to run. "
    from ella.core.signals import content_published, content_unpublished
    from ella_comments.listing_handlers import publishable_published, publishable_unpublished

    content_published.disconnect(publishable_published)
    content_unpublished.disconnect(publishable_unpublished)

def migrate_legacy_comments():
    CommentModel = comments.get_model()
    if not CommentModel._meta.installed:
        return

    cnt = 0
    for c in CommentModel.objects.exclude(user__isnull=True).order_by('submit_date').iterator():
        fc = FlatComment(
            site_id=c.site_id,
            content_type_id=c.content_type_id,
            object_id=c.object_pk,

            submit_date=c.submit_date,
            user=c.user,
            comment=c.comment,

            is_public=c.is_public and not c.is_removed,
        )

        fc.post()
        cnt += 1
    return cnt
