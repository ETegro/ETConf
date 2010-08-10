include Makefile.config

sync-debug:
ifeq ($(DEBUG), yes)
	sed -i "s/^DEBUG = .*$$/DEBUG = True/" settings.py
	sed -i "s/^TEMPLATE_DEBUG = .*$$/TEMPLATE_DEBUG = DEBUG/" settings.py
else
	sed -i "s/^DEBUG = .*$$/DEBUG = False/" settings.py
	sed -i "s/^TEMPLATE_DEBUG = .*$$/TEMPLATE_DEBUG = False/" settings.py
endif

sync-cache-backend:
	sed -i "s/^CACHE_BACKEND = .*$$/CACHE_BACKEND = '$(shell echo $(MEMCACHED_URL) | sed 's/\//\\\//g')'/" settings.py

sync-images:
	sed -i "s/^IMAGES_PATH = .*$$/IMAGES_PATH = '$(shell echo $(IMAGES_PATH) | sed 's/\//\\\//g')'/" settings.py

sync-fonts:
	sed -i "s/^FONTS_PATH = .*$$/FONTS_PATH = '$(shell echo $(FONTS_PATH) | sed 's/\//\\\//g')'/" settings.py

sync-stylesheet:
	sed -i "s/^STYLE_PATH = .*$$/STYLE_PATH = '$(shell echo $(STYLE_PATH) | sed 's/\//\\\//g')'/" settings.py

ifeq ($(DB_TYPE), mysql)
mysql-clean:
	echo "show tables" | mysql -u$(DB_USER) $(DB_NAME) | perl -ne 'chop; print "drop table $$_;\n" if /^(django|creator|carter|auth)/' | mysql -u$(DB_USER) $(DB_NAME)

sync-base: mysql-clean
	sed -i "s/^DATABASE_ENGINE = .*$$/DATABASE_ENGINE = 'mysql'/" settings.py
	sed -i "s/^DATABASE_NAME = .*$$/DATABASE_NAME = '$(DB_NAME)'/" settings.py
	sed -i "s/^DATABASE_USER = .*$$/DATABASE_USER = '$(DB_USER)'/" settings.py
	sed -i "s/^DATABASE_PASSWORD = .*$$/DATABASE_PASSWORD = '$(DB_PASSWORD)'/" settings.py
	sed -i "s/^DATABASE_HOST = .*$$/DATABASE_HOST = '$(DB_HOST)'/" settings.py
	sed -i "s/^DATABASE_PORT = .*$$/DATABASE_PORT = '$(DB_PORT)'/" settings.py
else
postgresql-clean:
	echo "DROP DATABASE $(DB_NAME); CREATE DATABASE $(DB_NAME)" | psql -U $(DB_USER)

sync-base: postgresql-clean
	sed -i "s/^DATABASE_ENGINE = .*$$/DATABASE_ENGINE = 'postgresql_psycopg2'/" settings.py
	sed -i "s/^DATABASE_NAME = .*$$/DATABASE_NAME = '$(DB_NAME)'/" settings.py
	sed -i "s/^DATABASE_USER = .*$$/DATABASE_USER = '$(DB_USER)'/" settings.py
	sed -i "s/^DATABASE_PASSWORD = .*$$/DATABASE_PASSWORD = '$(DB_PASSWORD)'/" settings.py
	sed -i "s/^DATABASE_HOST = .*$$/DATABASE_HOST = '$(DB_HOST)'/" settings.py
	sed -i "s/^DATABASE_PORT = .*$$/DATABASE_PORT = '$(DB_PORT)'/" settings.py
endif

syncdb:
	$(CMD_MANAGE) syncdb --noinput

sync-admin:
	$(CMD_MANAGE) createsuperuser --username=admin --email=admin@company.com

sync: sync-debug sync-images sync-fonts sync-stylesheet sync-cache-backend sync-base syncdb sync-admin

shell:
	$(CMD_MANAGE) shell

example:
	$(CMD_MANAGE) loaddata example
	$(CMD_MANAGE) loaddata orders

start:
	$(CMD_MANAGE) runserver

test:
	$(CMD_MANAGE) test giver

dump:
	$(CMD_MANAGE) dumpdata --format=json --indent=2 creator > creator/fixtures/example.json
	$(CMD_MANAGE) dumpdata --format=json --indent=2 carter > carter/fixtures/orders.json

translation:
	$(CMD_MANAGE) makemessages -l ru
	$(CMD_MANAGE) makemessages -d djangojs -l ru
	$(CMD_MANAGE) compilemessages
