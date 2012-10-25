from ella.utils.settings import Settings

MOST_COMMENTED_LH = 'most_commented'
RECENTLY_COMMENTED_LH = 'recently_commented'
LAST_COMMENTED_LH = 'last_commented'

# list of Comments-related ListingHandlers
LISTING_HANDLERS = (MOST_COMMENTED_LH, RECENTLY_COMMENTED_LH, LAST_COMMENTED_LH)

# redis client kwargs
REDIS = {}

comments_settings = Settings('ella_flatcomments.conf', 'COMMENTS')
