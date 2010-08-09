# ETConf -- web-based user-friendly computer hardware configurator
# Copyright (C) 2010 ETegro Technologies, PLC <http://www.etegro.com/>
#                    Sergey Matveev <sergey.matveev@etegro.com>
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

urlpatterns = patterns( "configurator.carter.views",
	( r"^order/create/(?P<computermodel_alias>.+)/$", "order_create" ),
	( r"^order/show/$", "order_show" ),
	( r"^order/remove/(?P<order_id>\d+)/$", "order_remove" ),
)
