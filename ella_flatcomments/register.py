from ella.core.models import Listing, Publishable
from ella.core.cache.redis import SlidingListingHandler
from ella.core.signals import content_published, content_unpublished

from ella_flatcomments.conf import comments_settings
from ella_flatcomments.signals import comment_was_posted, comment_was_moderated

LISTING_HANDLERS = None

def _get_listing_handlers():
    global LISTING_HANDLERS
    if LISTING_HANDLERS is None:
        LISTING_HANDLERS = tuple(lh for lh in (Listing.objects.get_listing_handler(k, fallback=False) for k in comments_settings.LISTING_HANDLERS) if lh is not None)
    return LISTING_HANDLERS


def comment_moderated(comment, user, **kwargs):
    # update the listing handlers
    obj = comment.content_object
    if isinstance(obj, Publishable) and obj.is_published():
        publishable_published(obj, delta=-1)


def comment_posted(comment, request, **kwargs):
    # update the listing handlers
    obj = comment.content_object
    if isinstance(obj, Publishable) and obj.is_published():
        publishable_published(obj, delta=1)


def publishable_unpublished(publishable, **kwargs):
    pipe = None
    for lh in _get_listing_handlers():
        pipe = lh.remove_publishable(publishable.category, publishable, pipe=pipe, commit=False)
    if pipe:
        pipe.execute()


def publishable_published(publishable, delta=0, **kwargs):
    pipe = None
    for lh in _get_listing_handlers():
        if issubclass(lh, SlidingListingHandler):
            if delta != 0:
                pipe = lh.incr_score(publishable.category, publishable, incr_by=delta, pipe=pipe, commit=False)
        else:
            pipe = lh.add_publishable(publishable.category, publishable, pipe=pipe, commit=False)
    if pipe:
        pipe.execute()

content_published.connect(publishable_published)
content_unpublished.connect(publishable_unpublished)

comment_was_posted.connect(comment_posted)
comment_was_moderated.connect(comment_moderated)
