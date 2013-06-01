# -*- coding: utf-8 -*-

# Django settings for the mozillians project.
import logging
import os.path
import sys

from funfactory.manage import path
from funfactory import settings_base as base
from settings import MEDIA_URL, MEDIA_ROOT
from urlparse import urljoin

from apps.users.helpers import calculate_username
from django.utils.functional import lazy

## Log settings
SYSLOG_TAG = "http_app_mozillians"
LOGGING = {
    'loggers': {
        'landing': {'level': logging.INFO},
        'phonebook': {'level': logging.INFO},
    },
}

## L10n
LOCALE_PATHS = [path('locale')]

# Accepted locales
PROD_LANGUAGES = ('ca', 'cs', 'de', 'en-US', 'es', 'hu', 'fr', 'it', 'ko',
                  'nl', 'pl', 'pt-BR', 'ru', 'sk', 'sl', 'sq', 'zh-TW',
                  'zh-CN', 'lt', 'ja')

# List of RTL locales known to this project. Subset of LANGUAGES.
RTL_LANGUAGES = ()  # ('ar', 'fa', 'fa-IR', 'he')

# For absoluate urls
PROTOCOL = "https://"
PORT = 443

## Media and templates.

STATIC_ROOT = path('media/static')
STATIC_URL = MEDIA_URL + 'static/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'jingo.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (base.TEMPLATE_CONTEXT_PROCESSORS +
    ('django_browserid.context_processors.browserid_form',))

JINGO_EXCLUDE_APPS = [
    'bootstrapform',
    'admin',
    'autocomplete_light'
]

MINIFY_BUNDLES = {
    'css': {
        'common': (
            'css/bootstrap.css',
            'css/jquery-ui-1.8.16.custom.css',
            'js/libs/tag-it/css/jquery.tagit.css',
            'css/base.css',
            'css/bootstrap-responsive.css',
            'css/base-480px.css',
            'css/base-768px.css',
            'css/base-980px.css',
        ),
        'api': (
            'css/prettify.css',
        ),
        'test': (
            'css/qunit.css',
        ),
        'edit_profile': (
            'css/user.css',
        ),
        'register': (
            'css/register.css',
        ),
    },
    'js': {
        'common': (
            'js/libs/jquery-1.7.2.js',
            'js/libs/jquery-ui-1.8.7.custom.min.js',
            'js/libs/bootstrap/bootstrap-transition.js',
            'js/libs/bootstrap/bootstrap-alert.js',
            'js/libs/bootstrap/bootstrap-modal.js',
            'js/libs/bootstrap/bootstrap-dropdown.js',
            'js/libs/bootstrap/bootstrap-tooltip.js',
            'js/libs/bootstrap/bootstrap-popover.js',
            'js/libs/bootstrap/bootstrap-button.js',
            'js/libs/bootstrap/bootstrap-collapse.js',
            'js/libs/bootstrap/bootstrap-carousel.js',
            'js/libs/bootstrap/bootstrap-typeahead.js',
            'js/libs/bootstrap/bootstrap-tab.js',
            'js/libs/validation/validation.js',
            'js/main.js',
            'static/browserid/browserid.js',
            'js/groups.js',
        ),
        'api': (
            'js/libs/prettify.js',
            'js/api.js',
        ),
        'edit_profile': (
            'js/libs/tag-it/js/tag-it.js',
            'js/profile_edit.js'
        ),
        'register': (
            'js/libs/tag-it/js/tag-it.js',
            'js/register.js',
        ),
        'search': (
            'js/libs/jquery.endless-scroll.js',
            'js/infinite.js',
            'js/expand.js',
        ),
        'backbone': (
            'js/libs/underscore.js',
            'js/libs/backbone.js',
            'js/libs/backbone.localStorage.js',
            'js/profiles.js',
        ),
        'test': (
            'js/libs/qunit.js',
            'js/tests/test.js',
        ),
        'profile_view': (
            'js/profile_view.js',
            ),
    }
}

MIDDLEWARE_CLASSES = list(base.MIDDLEWARE_CLASSES) + [
    'commonware.response.middleware.StrictTransportMiddleware',
    'csp.middleware.CSPMiddleware',

    'django_statsd.middleware.GraphiteMiddleware',
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.TastyPieRequestTimingMiddleware',

    'common.middleware.StrongholdMiddleware',
    'common.middleware.UsernameRedirectionMiddleware',
    'common.middleware.OldGroupRedirectionMiddleware',
    'common.middleware.GroupAliasRedirectionMiddleware']

# StrictTransport
STS_SUBDOMAINS = True

# Not all URLs need locale.
SUPPORTED_NONLOCALES = list(base.SUPPORTED_NONLOCALES) + [
    'csp',
    'api',
    'browserid',
    'admin',
    'autocomplete'
]

AUTHENTICATION_BACKENDS = ('common.backends.MozilliansBrowserID',)

# BrowserID creates a user if one doesn't exist.
BROWSERID_CREATE_USER = True
BROWSERID_USERNAME_ALGO = calculate_username

# On Login, we redirect through register.
LOGIN_REDIRECT_URL = '/register'

INSTALLED_APPS = list(base.INSTALLED_APPS) + [
    # These need to go in order of migration.
    'users',
    'phonebook',
    'groups',
    'common',
    'api',
    'mozspaces',

    'csp',
    'jingo_minify',
    'tower',
    'cronjobs',
    'elasticutils',
    'sorl.thumbnail',
    'autocomplete_light',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.staticfiles',
    'django_browserid',
    'bootstrapform',

    # DB migrations
    'south',
    # re-assert dominance of 'django_nose'
    'django_nose',
]

## Auth
PWD_ALGORITHM = 'bcrypt'
HMAC_KEYS = {
    '2011-01-01': 'cheesecake',
}

SESSION_COOKIE_HTTPONLY = True
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
ANON_ALWAYS = True

# Email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
FROM_NOREPLY = u'Mozillians <no-reply@mozillians.org>'

# Auth
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

AUTH_PROFILE_MODULE = 'users.UserProfile'

MAX_PHOTO_UPLOAD_SIZE = 8 * (1024 ** 2)

AUTO_VOUCH_DOMAINS = ('mozilla.com', 'mozilla.org', 'mozillafoundation.org')
SOUTH_TESTS_MIGRATE = False

# Django-CSP
CSP_IMG_SRC = ("'self'", 'http://www.google-analytics.com',
               'https://ssl.google-analytics.com',
               'http://www.gravatar.com',
               'https://i1.wp.com',
               'https://secure.gravatar.com',)
CSP_SCRIPT_SRC = ("'self'", 'http://www.google-analytics.com',
                  'https://ssl.google-analytics.com',
                  'https://www.google-analytics.com',
                  'https://browserid.org',
                  'https://login.persona.org',)
CSP_FRAME_SRC = ("'self'", 'https://browserid.org',
                 'https://login.persona.org',)
CSP_FONT_SRC = ("'self'", 'https://www.mozilla.org')
CSP_REPORT_ONLY = True
CSP_REPORT_URI = '/csp/report/'

ES_DISABLED = True
ES_HOSTS = ['127.0.0.1:9200']
ES_INDEXES = dict(default='mozillians')
ES_INDEXING_TIMEOUT = 10

# Sorl settings
THUMBNAIL_DUMMY = True
THUMBNAIL_PREFIX = 'uploads/sorl-cache/'

# Statsd Graphite
STATSD_CLIENT = 'django_statsd.clients.normal'

# Basket
# If we're running tests, don't hit the real basket server.
if 'test' in sys.argv:
    BASKET_URL = 'http://127.0.0.1'
else:
    BASKET_URL = 'http://basket.mozilla.com'
BASKET_NEWSLETTER = 'mozilla-phone'

USER_AVATAR_DIR = 'uploads/userprofile'
MOZSPACE_PHOTO_DIR = 'uploads/mozspaces'

# Google Analytics
GA_ACCOUNT_CODE = 'UA-35433268-19'

# Set ALLOWED_HOSTS based on SITE_URL.
def _allowed_hosts():
    from django.conf import settings
    from urlparse import urlparse

    host = urlparse(settings.SITE_URL).netloc # Remove protocol and path
    host = host.rsplit(':', 1)[0]  # Remove port
    return [host]
ALLOWED_HOSTS = lazy(_allowed_hosts, list)()

STRONGHOLD_EXCEPTIONS = ['^%s' % MEDIA_URL,
                         '^/csp/',
                         '^/admin/',
                         '^/browserid/verify/',
                         '^/api']

# Set default avatar for user profiles
DEFAULT_AVATAR= 'img/unknown.png'
DEFAULT_AVATAR_URL = urljoin(MEDIA_URL, DEFAULT_AVATAR)
DEFAULT_AVATAR_PATH = os.path.join(MEDIA_ROOT, DEFAULT_AVATAR)
