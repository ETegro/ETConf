LANGUAGE_CODE = 'en'
################################################################################
# Cofigurator related options
################################################################################
DEBUG = True
TEMPLATE_DEBUG = True

DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'sggal'
DATABASE_USER = 'root'
DATABASE_PASSWORD = 'root'
DATABASE_HOST = ''
DATABASE_PORT = ''

CART_COOKIE_NAME = "configurator-cart"

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
CACHE_MIDDLEWARE_SECONDS = 1800
CACHE_MIDDLEWARE_KEY_PREFIX = ""

IMAGES_PATH = '/var/www/etegro2/www/img'
FONTS_PATH = '/home/asapronov/fonts'
STYLE_PATH = '/var/www/etegro2/configurator/media/rst2pdf-stylesheet.style'

ORDER_SUBJECT_FROM = "etegro.com"
ORDER_FROM = "sales@etegro.com"
ORDER_CC = "www@etegro.com"

################################################################################
# Django application related options
################################################################################
DEFAULT_CONTENT_TYPE = "text/html" # Should be "application/xhtml+xml"
SESSION_COOKIE_NAME = "configurator-sessionid"
LOGIN_URL = "/wizard/admin"

ADMINS = (
	('Sergey Matveev', 'sergey.matveev@etegro.com'),
)

AUTH_PROFILE_MODULE = "partners.PartnerProfile"
MANAGERS = ADMINS

TIME_ZONE = 'Europe/Moscow'
LANGUAGE_CODE = 'en'
SITE_ID = 1
USE_I18N = True
MEDIA_ROOT = ''
MEDIA_URL = '/static/configurator/'
ADMIN_MEDIA_PREFIX = '/static/configurator/admin/'
SECRET_KEY = 'fg)5$644e!=-ckg#*6aqghx-c#q7^i(%ui&8bdgq#whtseee-t'
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
