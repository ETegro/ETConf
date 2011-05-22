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

from django.contrib import admin
from configurator.carter.models import *
from django.utils.translation import ugettext as _

class OrderRequestAdmin( admin.ModelAdmin ):
	date_hierarchy = "created"
	ordering = [ "created", "name", "company" ]
	search_fields = [ "name", "company", "email", "telephone", "body" ]
	list_display = [ "name", "company", "created", "pred_body" ]
	list_filter = [ "created", "name", "company" ]
	def pred_body( self, order_request ):
		return "<pre>%s</pre>" % order_request.body.replace("<","&lt;").replace(">","&gt;")
	pred_body.allow_tags = True
	pred_body.short_description = _("Body")

admin.site.register( OrderRequest, OrderRequestAdmin )
