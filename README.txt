                                 ======
                                 ETConf
                                 ======
                                    
                                Summary
                                =======
Web-based user-friendly interface that is intended to build-up
your computer's hardware configuration from different components in
real-time (AJAX) with necessary validation of all requirements and
compatibilities between components.

It heavily uses AJAX technology to lower delays between user's
actions. It is written on Django framework[1] and needed to be
run under FastCGI or WSGI compatible HTTP server. Also, overall
architecture is heavily influenced by ETegro Technologies company[2]
needs.

ETConf can validate hardware configuration, preventing user from
creating either uncompatible or incorrect machine. Also, ETConf
provides ability to store build-up computers in cart and to provide
order request for salesmen.

                                License
                                =======
ETConf is free software and is licensed under GNU Affero GPL version 3
or higher.

                             Example usage
                             =============
* Costumer willing to buy a server visits some company's catalogue
* Simultaneously configurator's window is loading using AJAX technology
* Costumer selects necessary components and their quantities, seeing
  price and overall configuration update in real-time. He can not create
  either invalid or incorrect hardware configuration
* Costumer pushes "Add to cart" button and follows redirection to his
  cart. He can repeat new computers adding to it
* When he is either tired or out of money, he can request an order, by
  pushing corresponding button in his cart. He will be asked his name,
  email, and other additional useful information
* Confirmation email to salesmen, costumer will be sent. His order will
  be saved in database to not to lost it

                                Features
                                ========
* Validation of component's compatibilities, requirements and
  correctnesss of overall configuration
* User-friendly simple web-based AJAX real-time interface, preventing
  user to create invalid configurations
* Manager-friendly administration interface to create and modify
  computer's configurations
* Ability to use so-called "conversions" like Google AdWords does (just
  simple raw small ECMAScripts included where they need to be)
* Ability to produce PDF documents with computer overview
* Ability to generate Yandex Market service's[3] YMLs
* Using of reStructured Text[4] in description of various objects

                              Translations
                              ------------
* English
* Russian

                      Internal structure overview
                      ===========================
The main object in this configurator is "Computer model". As a rule it
is some base of server/computer that can has different CPUs, different
quantity of memory, different controllers and so on. Every computer
model has it's name, description, alias (unique name -- computer model's
main identification string), related hardware components that can be
used together with that server and maybe many specification pairs.

Specification is a simple pair of key -- value. Key can be something
like "Dimensions", and value can be something like "20x35x40".

Component is the most complicated part of configurator. Component has
name, description, price, so-called "component group" (for example
component with the name "DDR3 1GB" will be in group "RAM"). Nearly every
component has some requirements to work, to be able to be inserted,
plugged in, etc. For example you have to provide enclosure and SATA
interface cable to make SATA HDD working. SATA interface and enclosure
are called "features". Nearly every component requires some features and
can provide the new ones.

You have an empty platform for your server. It consists of single lonely
motherboard. It provides different various interfaces and slots for
expansion cards. But it requires nothing. Your case also requires
nothing and provides several HDD enclosures. You want to use SAS HDD
with your server, but motherboard has only SATA interface. Configurator
won't allow you to inset SAS drive, but it will allow you to insert SAS
controller. It requires PCIe slot. Motherboard has it -- so you can
insert SAS controller and after that configurator will allow you to
insert SAS HDD.

Next thing. Some features can duplicate each other in one way. You can
use low profile PCIe expansion cards with high profile PCIe slot. And of
course you can use high profile card with it. Of course you can just
duplicate all components and features creating ones for high profile and
the others for low profile computers. But it is not user-friendly and
can lead to huge quantity of mistakes. So, there is such objects as
"substitutions" where you can just tell what feature can replace the
other one.

Each requirement tells how many features someone needs to provide to be
able to fitful it. Also, some components can be used only in pairs or in
quantity of three. Of course you can specifify that component's
"parity".

Also, there are objects called "expanders". They act like a some kind of
network hub -- they increase number of needed features. It is not used
very often, but can be useful someday.

And last remark: all component groups can be grouped together in
so-called "subsystems".

                              Requirements
                              ============
* Python interpreter[5] 2.5 version or higher
* Django framework 1.1.1
* MySQL, PostgreSQL or SQLite database with correpsonding Python library
* Python YAML library
* Docutils to render reStructured Text
* GNU Make
* Memcache daemon with corresponding Python library for caching purposes
* Prototype.js[7] and Script.Aculo.Us[8] ECMAScript libraries

PDF generator uses rst2pdf command[6] to render them. You must have rst2pdf
program installed and fonts in some directory.

                   Example installation under Debian
                   ---------------------------------
  % apt-get install python-sqlite python python-docutils python-flup python-memcache python-psycopg2 python-yaml make python-mysql memcached python-setuptools build-essential libfreetype6-dev python-dev python-imaging
  % wget -O - http://www.djangoproject.com/download/1.1.1/tarball/ | gunzip -c | tar xvf -
  % pushd Django-1.1.1 && python setup.py install && popd && rm -fr Django-1.1.1
  % wget -O - http://rst2pdf.googlecode.com/files/rst2pdf-0.15.tar.gz | gunzip -c | tar xvf -
  % pushd rst2pdf-0.15 && python setup.py install && popd && rm -fr rst2pdf-0.15
  % cp -r /somewhere/fonts /tmp/fonts
  % sed -i "s/^FONTS_PATH=.*$$/FONTS_PATH=\/tmp\/fonts/" Makefile.config

                              Installation
                              ============
Because ETConf is written on an interpreted language -- there is no need
to compile anything in it. Just create database, edit Makefile.config,
make sync-DATABASE, configure your HTTP server and that is all.

If you want to use SQLite as database backend, then you should run "make
sync-sqlite". If you want to use either MySQL or PostgreSQL, then run
"make sync-mysql" or "make sync-postgresql". This will create all
necessary tables in database.

There is an example ETegro Technologies database of various server's
configurations. You can load it into database by "make example".

Next, put Prototype.js and Script.Aculo.Us JavaScript libraries into
shared static files directory.

                         Running under Lighttpd
                         ----------------------
To be filled.

                          Running under Apache
                          --------------------
The most easy way to run ETConf under Apache is to use WSGI interface.
Be sure to have necessary Apache's WSGI module installed, and add the
following example string into your configuration file:

  WSGIScriptAlias /configurator /path/to/configurator/django.wsgi

After that, your configurator will be available with URL's prefix
"/configurator".

                                 Notes
                                 =====
* Yandex Market's YML generator currently is very ETegro (and Russia
  overall) specific. Please look deeper into *marketer/* subdirectory
  if you need.  It's YML is available by /market.xml URL.

[1] http://www.djangoproject.com/
[2] http://www.etegro.com/
[3] http://market.yandex.ru/
[4] http://docutils.sourceforge.net/rst.html
[5] http://www.python.org/
[6] http://code.google.com/p/rst2pdf/
[7] http://www.prototypejs.org/
[8] http://script.aculo.us/
