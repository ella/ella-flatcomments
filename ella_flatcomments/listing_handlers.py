from ella.core.cache.redis import RedisListingHandler, SlidingListingHandler, TimeBasedListingHandler

from ella_flatcomments.models import CommentList

class RecentMostCommentedListingHandler(SlidingListingHandler):
    PREFIX = 'recently_commented'


class MostCommentedListingHandler(RedisListingHandler):
    PREFIX = 'most_commented'

    @classmethod
    def add_publishable(cls, category, publishable, score=None, pipe=None, commit=True):
        if score is None:
            score = CommentList(publishable.content_type, publishable.pk).count()
            # no comments yet, pass
            if not score:
                return pipe
        return super(MostCommentedListingHandler, cls).add_publishable(category, publishable, score, pipe=pipe, commit=commit)


class LastCommentedListingHandler(TimeBasedListingHandler):
    PREFIX = 'last_commented'

    @classmethod
    def add_publishable(cls, category, publishable, score=None, publish_from=None, pipe=None, commit=True):
        if score is None and publish_from is None:
            last_comment = CommentList.for_object(publishable).last_comment()
            # no comment yet, pass
            if last_comment is None:
                return pipe
            publish_from = last_comment.submit_date
        return super(LastCommentedListingHandler, cls).add_publishable(category, publishable, score=score, publish_from=publish_from, pipe=pipe, commit=commit)

