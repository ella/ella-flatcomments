from ella.core.models import Listing, Publishable
from ella.core.cache.redis import SlidingListingHandler

from ella_flatcomments.conf import comments_settings
from ella_flatcomments.models import CommentList

LISTING_HANDLERS = None

def _get_listing_handlers():
    global LISTING_HANDLERS
    if LISTING_HANDLERS is None:
        LISTING_HANDLERS = tuple(lh for lh in (Listing.objects.get_listing_handler(k, fallback=False) for k in comments_settings.LISTING_HANDLERS) if lh is not None)
    return LISTING_HANDLERS


def comment_moderated(comment, user, **kwargs):
    # remove comment from redis
    CommentList(comment.content_type, comment.object_id).remove_comment(comment)

    # update the listing handlers
    obj = comment.content_object
    if isinstance(obj, Publishable) and obj.is_published():
        publishable_published(obj, delta=-1)


def comment_posted(comment, request, **kwargs):
    # add comment to redis
    CommentList(comment.content_type, comment.object_id).add_comment(comment)

    # update the listing handlers
    obj = comment.content_object
    if isinstance(obj, Publishable) and obj.is_published():
        publishable_published(obj, delta=1)


def publishable_unpublished(publishable, **kwargs):
    pipe = None
    for lh in _get_listing_handlers():
        if issubclass(lh, SlidingListingHandler):
            continue
        lh.remove_publishable(publishable.category, publishable, pipe=pipe, commit=False)
    pipe.execute()


def publishable_published(publishable, delta=0, **kwargs):
    pipe = None
    for lh in _get_listing_handlers():
        if issubclass(lh, SlidingListingHandler):
            if delta != 0:
                lh.incr_score(publishable.category, publishable, incr_by=delta, pipe=pipe, commit=False)
        else:
            lh.add_publishable(publishable.category, publishable, pipe=pipe, commit=False)
    pipe.execute()
