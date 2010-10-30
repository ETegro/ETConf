============
Конфигуратор
============

Что необходимо для работы
=========================
* Python версии не ниже 2.5
* Django версии не ниже 1.1.1
* MySQL/PostgreSQL/SQLite библиотеки для Python
* YAML библиотека для Python
* Docutils для отображения reStructured Text-а
* GNU Make
* Демон кэширующего сервера Memcache
* Библиотека Memcache для Python-а

Для генерирования PDF-ок моделей
--------------------------------
* rst2pdf программа
* шрифты с русским языком

Пример установки под Debian
---------------------------

  % apt-get install python-sqlite python python-docutils python-flup python-memcache python-psycopg2 python-yaml make python-mysql memcached python-setuptools build-essential libfreetype6-dev python-dev python-imaging
  % wget -O - http://www.djangoproject.com/download/1.1.1/tarball/ | gunzip -c | tar xvf -
  % pushd Django-1.1.1 && python setup.py install && popd && rm -fr Django-1.1.1
  % wget -O - http://rst2pdf.googlecode.com/files/rst2pdf-0.15.tar.gz | gunzip -c | tar xvf -
  % pushd rst2pdf-0.15 && python setup.py install && popd && rm -fr rst2pdf-0.15
  % svn export svn+ssh://subversion.etegro.local/var/lib/subversion/manufacturing/trunk/doc-build-system/fonts /tmp/fonts
  % sed -i "s/^FONTS_PATH=.*$$/FONTS_PATH=\/tmp\/fonts/" Makefile.config

Как запустить
=============

Настроить базу данных
---------------------
Просто достаточно правильно заполнить поля в ``Makefile.config''.

Сгенерировать базу данных
-------------------------
Выполнить ``make sync-sqlite'' или ``make sync-mysql'', при этом
будет спрошен пароль для пользователя который будет модифицировать
базу в административном интерфейсе.  Пользователь ``etegro''.

Загрузить примерную базу данных
-------------------------------
Если необходимо загрузить базу данных-пример, то достаточно выполнить
``make example''. 

Генерирование примерной базы данных
___________________________________
После заполнения онной, выполнить ``make dump'' который выбросит текущую
базу данных в формате JSON в ``creator/fixtures/example.json''.

Запуск standalone версии
------------------------
Выполнить ``make start''. Будет написан адрес по которому можно будет
зайти чтобы попасть в конфигуратор.

``/admin'' -- для административного интерфейса.

Запуск за Apache-ем
-------------------
.. warning::
   Конфигуратор требует абсолютных путей в своих конфигурационных
   файлов! Будьте внимательны при указании пути для SQLite файла базы
   данных.

В конфигурационном файле Apache-е надо указать как запускать
Конфигуратор через WSGI интерфейс. Соответственно нужен модуль.
 
  WSGIScriptAlias /wizard /path/to/configurator/django.wsgi

После запуска, по URL-е с префиксом ``/wizard'' перед обычно
используемыми до этого можно будет попасть в него (как в
административную панель, так и в другое место).

Заметки
=======
Цена на сервер по умолчанию
---------------------------
Цена для сервера по умолчанию в текущей по умолчанию валюте находится
для каждого сервера в таблице ``creator_computermodel'' в поле
``default_price''. При изменении:
