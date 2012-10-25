from ella.core.models import Listing
from ella.core.cache.redis import RedisListingHandler, SlidingListingHandler
from ella.utils.timezone import to_timestamp

from ella_flatcomments.models import CommentList

class CommentListingHandlerMixin(object):
    def _get_score_limits(self):
        max_score = None
        min_score = None

        if self.date_range:
            raise NotSupported()
        return min_score, max_score

    def _get_listing(self, publishable, score):
        return Listing(publishable=publishable, publish_from=publishable.publish_from)

class RecentMostCommentedListingHandler(CommentListingHandlerMixin, SlidingListingHandler):
    PREFIX = 'recent_comcount'


class MostCommentedListingHandler(CommentListingHandlerMixin, RedisListingHandler):
    PREFIX = 'comcount'

    @classmethod
    def add_publishable(cls, category, publishable, score=None, pipe=None, commit=True):
        if score is None:
            score = CommentList(publishable.content_type, publishable.pk).count()
        super(MostCommentedListingHandler, cls).add_publishable(category, publishable, score, pipe=pipe, commit=commit)


class LastCommentedListingHandler(CommentListingHandlerMixin, RedisListingHandler):
    PREFIX = 'lastcommented'
    @classmethod
    def add_publishable(cls, category, publishable, score=None, pipe=None, commit=True):
        if score is None:
            score = repr(to_timestamp(CommentList(publishable.content_type, publishable.pk)[0].submit_date))
        super(LastCommentedListingHandler, cls).add_publishable(category, publishable, score, pipe=pipe, commit=commit)

