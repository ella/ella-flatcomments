from datetime import datetime

from ella.core.models import Listing

from ella_flatcomments.conf import comments_settings
from ella_flatcomments.models import FlatComment

from test_ella_flatcomments.cases import PublishableTestCase

from nose import tools

class TestListingHandlers(PublishableTestCase):
    def test_most_commented_lh_doesnt_include_uncommented_publishable(self):
        lh = Listing.objects.get_queryset_wrapper(self.category_nested, source=comments_settings.MOST_COMMENTED_LH)

        tools.assert_equals(0, lh.count())

    def test_recently_most_commented_lh_doesnt_include_uncommented_publishable(self):
        lh = Listing.objects.get_queryset_wrapper(self.category_nested, source=comments_settings.RECENTLY_COMMENTED_LH)

        tools.assert_equals(0, lh.count())

    def test_last_commented_lh_doesnt_include_uncommented_publishable(self):
        lh = Listing.objects.get_queryset_wrapper(self.category_nested, source=comments_settings.LAST_COMMENTED_LH)

        tools.assert_equals(0, lh.count())


    def test_last_commented_finds_the_publishable_with_comments_time(self):
        submit_date = datetime(2010, 10, 10)
        c = self._get_comment(submit_date=submit_date)
        FlatComment.objects.post_comment(c, None)

        lh = Listing.objects.get_queryset_wrapper(self.category_nested, source=comments_settings.LAST_COMMENTED_LH)

        tools.assert_equals(1, lh.count())
        listing = lh[0]
        tools.assert_equals(submit_date, listing.publish_from)
