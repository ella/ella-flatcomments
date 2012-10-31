from ella.core.cache.redis import RedisListingHandler, SlidingListingHandler, TimeBasedListingHandler

from ella_flatcomments.models import CommentList

class RecentMostCommentedListingHandler(SlidingListingHandler):
    PREFIX = 'recent_comcount'


class MostCommentedListingHandler(RedisListingHandler):
    PREFIX = 'comcount'

    @classmethod
    def add_publishable(cls, category, publishable, score=None, pipe=None, commit=True):
        if score is None:
            score = CommentList(publishable.content_type, publishable.pk).count()
            # no comments yet, pass
            if not score:
                return pipe
        return super(MostCommentedListingHandler, cls).add_publishable(category, publishable, score, pipe=pipe, commit=commit)


class LastCommentedListingHandler(TimeBasedListingHandler):
    PREFIX = 'lastcommented'

    @classmethod
    def add_publishable(cls, category, publishable, score=None, publish_from=None, pipe=None, commit=True):
        if score is None and publish_from is None:
            try:
                publish_from = CommentList(publishable.content_type, publishable.pk)[0].submit_date
            except IndexError:
                # no comment yet, pass
                return pipe
        return super(LastCommentedListingHandler, cls).add_publishable(category, publishable, score=score, publish_from=publish_from, pipe=pipe, commit=commit)

