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

sqlite-clean:
	rm -f $(SQLITE_DB_PATH)

mysql-clean:
	echo "show tables" | mysql -u$(MYSQL_USER) $(MYSQL_NAME) | perl -ne 'chop; print "drop table $$_;\n" if /^(django|creator|carter|auth)/' | mysql -u$(MYSQL_USER) $(MYSQL_NAME)

sync-base-sqlite: sqlite-clean
	echo "WARNING: This target is only for SQlite-based database"
	sed -i "s/^DATABASE_ENGINE = .*$$/DATABASE_ENGINE = 'sqlite3'/" settings.py
	sed -i "s/^DATABASE_NAME = .*$$/DATABASE_NAME = '$(shell echo $(SQLITE_DB_PATH) | sed 's/\//\\\//g')'/" settings.py
	touch $(SQLITE_DB_PATH)
	chmod 666 $(SQLITE_DB_PATH)

sync-base-mysql: mysql-clean
	echo "WARNING: This target is only for MySQL-based database"
	sed -i "s/^DATABASE_ENGINE = .*$$/DATABASE_ENGINE = 'mysql'/" settings.py
	sed -i "s/^DATABASE_NAME = .*$$/DATABASE_NAME = '$(MYSQL_NAME)'/" settings.py
	sed -i "s/^DATABASE_USER = .*$$/DATABASE_USER = '$(MYSQL_USER)'/" settings.py
	sed -i "s/^DATABASE_PASSWORD = .*$$/DATABASE_PASSWORD = '$(MYSQL_PASSWORD)'/" settings.py
	sed -i "s/^DATABASE_HOST = .*$$/DATABASE_HOST = '$(MYSQL_HOST)'/" settings.py
	sed -i "s/^DATABASE_PORT = .*$$/DATABASE_PORT = '$(MYSQL_PORT)'/" settings.py

postgresql-clean:
	echo "DROP DATABASE $(MYSQL_NAME); CREATE DATABASE $(MYSQL_NAME)" | psql -U $(MYSQL_USER)

sync-base-postgresql: postgresql-clean
	echo "WARNING: This target is only for PostgreSQL-based database"
	sed -i "s/^DATABASE_ENGINE = .*$$/DATABASE_ENGINE = 'postgresql_psycopg2'/" settings.py
	sed -i "s/^DATABASE_NAME = .*$$/DATABASE_NAME = '$(MYSQL_NAME)'/" settings.py
	sed -i "s/^DATABASE_USER = .*$$/DATABASE_USER = '$(MYSQL_USER)'/" settings.py
	sed -i "s/^DATABASE_PASSWORD = .*$$/DATABASE_PASSWORD = '$(MYSQL_PASSWORD)'/" settings.py
	sed -i "s/^DATABASE_HOST = .*$$/DATABASE_HOST = '$(MYSQL_HOST)'/" settings.py
	sed -i "s/^DATABASE_PORT = .*$$/DATABASE_PORT = '$(MYSQL_PORT)'/" settings.py

syncdb:
	$(CMD_MANAGE) syncdb --noinput

sync-admin:
	$(CMD_MANAGE) createsuperuser --username=etegro --email=etegro@etegro.com

sync-sqlite: sync-debug sync-images sync-fonts sync-stylesheet sync-cache-backend sync-base-sqlite syncdb sync-admin
sync-mysql: sync-debug sync-images sync-fonts sync-stylesheet sync-cache-backend sync-base-mysql syncdb sync-admin
sync-postgresql: sync-debug sync-images sync-fonts sync-stylesheet sync-cache-backend sync-base-postgresql syncdb sync-admin

shell:
	echo "from configurator.creator.models import *"
	echo "from configurator.giver.views import *"
	echo "from configurator.carter.models import *"
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
