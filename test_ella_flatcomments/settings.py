DEBUG = True

ROOT_URLCONF = 'test_ella_flatcomments.urls'
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

TEMPLATE_LOADERS = (
    'secure.test_helpers.template_loader.load_template_source',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
)


SECRET_KEY = 'very-secret'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.redirects',
    'django.contrib.admin',

    'ella.core',
    'ella.photos',
    'ella.articles',

    'ella_flatcomments',
)

SITE_ID = 1

LISTING_HANDLERS = {
    'default': 'ella.core.cache.redis.TimeBasedListingHandler',

    'most_commented': 'ella_flatcomments.listing_handlers.MostCommentedListingHandler',
    'recently_commented': 'ella_flatcomments.listing_handlers.RecentMostCommentedListingHandler',
    'last_commented': 'ella_flatcomments.listing_handlers.LastCommentedListingHandler',
}
USE_REDIS_FOR_LISTINGS = True
LISTINGS_REDIS = REDIS = COMMENTS_REDIS = {}
COMMENTS_PAGINATE_BY = 2
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
