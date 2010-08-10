################################################################################
# Cofigurator related options
################################################################################
DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'to be filled'
DATABASE_NAME = 'to be filled'
DATABASE_USER = 'to be filled'
DATABASE_PASSWORD = 'to be filled'
DATABASE_HOST = 'to be filled'
DATABASE_PORT = 'to be filled'

CACHE_TIMEOUT = 1800
CART_COOKIE_NAME = "configurator-cart"

CACHE_BACKEND = 'to be filled'

IMAGES_PATH = 'to be filled'
FONTS_PATH = 'to be filled'
STYLE_PATH = 'to be filled'

ORDER_SUBJECT_FROM = "company.com"
ORDER_FROM = "sales@company.com"
ORDER_CC = "www@company.com"

################################################################################
# Django application related options
################################################################################
DEFAULT_CONTENT_TYPE = "text/html" # Should be "application/xhtml+xml"
SESSION_COOKIE_NAME = "configurator-sessionid"
LOGIN_URL = "/configurator/admin"

ADMINS = (
	('Your admin', 'your.admin@company.com'),
)

MANAGERS = ADMINS

TIME_ZONE = 'Europe/Moscow'
LANGUAGE_CODE = 'en'
SITE_ID = 1
USE_I18N = True
MEDIA_ROOT = ''
MEDIA_URL = '/static/configurator/'
ADMIN_MEDIA_PREFIX = '/static/configurator/admin/'
SECRET_KEY = '5f(1=0i$)#s_=^xsk&hii#mb37#2iqiz0is+y5-kzl&6^0=t!@'

TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.load_template_source',
	'django.template.loaders.app_directories.load_template_source',
#	'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.cache.UpdateCacheMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.middleware.cache.FetchFromCacheMiddleware'
)

ROOT_URLCONF = 'configurator.urls'

TEMPLATE_DIRS = (
)

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.admin',
	'django.contrib.markup',
	'django.contrib.humanize',
	'configurator.creator',
	'configurator.giver',
	'configurator.carter',
	'configurator.marketer',
	'configurator',
)
