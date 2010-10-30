# ETConf -- web-based user-friendly computer hardware configurator
# Copyright (C) 2010-2011 ETegro Technologies, PLC <http://etegro.com/>
#                         Sergey Matveev <sergey.matveev@etegro.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

js_info_dict = { "packages": ( "configurator" ) }

urlpatterns = patterns('',
    ( r'^admin/', include( admin.site.urls ) ),
    ( r'^creator/', include( "configurator.creator.urls" ) ),
    ( r'^giver/', include( "configurator.giver.urls" ) ),
    ( r'^carter/', include( "configurator.carter.urls" ) ),
    ( r'^sessioner/', include( "configurator.sessioner.urls" ) ),
    ( r'^market.xml', include( "configurator.marketer.urls" ) ),
    ( r'^jsi18n/$', "django.views.i18n.javascript_catalog", js_info_dict ),
    ( r'^i18n/', include( "django.conf.urls.i18n" ) ),
)
