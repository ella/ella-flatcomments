from ella.core.models import Listing

from ella_flatcomments.conf import comments_settings

from test_ella_flatcomments.cases import PublishableTestCase

from nose import tools

class TestMostCommented(PublishableTestCase):
    def test_most_commented_lh_doesnt_include_uncommented_publishable(self):
        lh = Listing.objects.get_queryset_wrapper(self.category, source=comments_settings.MOST_COMMENTED_LH)

        tools.assert_equals(0, lh.count())

