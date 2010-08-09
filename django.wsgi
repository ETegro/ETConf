import os, sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'configurator.settings'

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path: sys.path.append(path)

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
