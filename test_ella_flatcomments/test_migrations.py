from datetime import datetime, timedelta
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.signals import comment_was_posted

from threadedcomments.models import ThreadedComment

from ella.core.models import Listing

from ella_flatcomments.utils import migrate_legacy_comments
from ella_flatcomments.conf import comments_settings

from nose import tools

from test_ella_flatcomments.cases import PublishableTestCase

def create_legacy_comment(obj, **kwargs):
    defaults = {
        'comment': '',
        'content_type': ContentType.objects.get_for_model(obj),
        'object_pk': obj.pk,
        'site': Site.objects.get_current(),
    }
    defaults.update(kwargs)
    c = ThreadedComment.objects.create(**defaults)
    comment_was_posted.send(c.__class__, comment=c, request=None)
    return c


class TestMigrations(PublishableTestCase):
    def setUp(self):
        super(TestMigrations, self).setUp()

        self.comments = []
        for x in range(10):
            self.comments.append(
                create_legacy_comment(
                        self.publishable,
                        user=self.user,
                        comment='%sth' % x,
                        submit_date=datetime.now() - timedelta(seconds=10 - x)
                    )
            )


    def test_comments_successfully_migrated(self):
        migrate_legacy_comments()

        tools.assert_equals(10, self.comment_list.count())
        c = self.comment_list.last_comment()
        tools.assert_equals('9th', c.comment)

    def test_listing_handlers_filled_during_migration(self):
        migrate_legacy_comments()
        lh = Listing.objects.get_queryset_wrapper(self.category_nested, source=comments_settings.MOST_COMMENTED_LH)
        tools.assert_equals(1, lh.count())
