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

ORDER_SUBJECT_FROM = "etegro.com"
ORDER_FROM = "sales@etegro.com"
ORDER_CC = "www@etegro.com"

################################################################################
# Django application related options
################################################################################
DEFAULT_CONTENT_TYPE = "text/html" # Should be "application/xhtml+xml"
SESSION_COOKIE_NAME = "configurator-sessionid"
LOGIN_URL = "/configurator/admin"

ADMINS = (
	('Sergey Matveev', 'sergey.matveev@etegro.com'),
)

AUTH_PROFILE_MODULE = "partners.PartnerProfile"
MANAGERS = ADMINS

TIME_ZONE = 'Europe/Moscow'
LANGUAGE_CODE = 'ru'
SITE_ID = 1
USE_I18N = True
MEDIA_ROOT = ''
MEDIA_URL = '/static/configurator/'
ADMIN_MEDIA_PREFIX = '/static/configurator/admin/'
SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
#SESSION_COOKIE_SECURE = True
SESSION_COOKIE_PATH = "/wizard"

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
	'configurator.partners',
	'configurator.sessioner',
	'configurator',
)
