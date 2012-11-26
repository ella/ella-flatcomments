from ella.utils.settings import Settings

MOST_COMMENTED_LH = 'most_commented'
RECENTLY_COMMENTED_LH = 'recently_commented'
LAST_COMMENTED_LH = 'last_commented'

# list of Comments-related ListingHandlers
LISTING_HANDLERS = (MOST_COMMENTED_LH, RECENTLY_COMMENTED_LH, LAST_COMMENTED_LH)

# redis client kwargs
REDIS = {}

LIST_KEY = 'comments:%s:%s:%s'
LOCKED_KEY = 'comments_locked'

PAGINATE_BY = 10

IS_MODERATOR_FUNC = lambda u: u.is_staff

comments_settings = Settings('ella_flatcomments.conf', 'COMMENTS')
