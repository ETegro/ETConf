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
from configurator.partners.models import *
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

class PersonalManagerAdmin( admin.ModelAdmin ):
	ordering = [ "name" ]
	list_display = [ "name" ]

class CityAdmin( admin.ModelAdmin ):
	ordering = [ "name" ]
	list_display = [ "name" ]

class PartnerProfileAdmin( admin.ModelAdmin ):
	list_display = [ "company_name",
			 "city",
			 "generic_formula",
			 "discount_action",
			 "personal_manager",
			 "link_to_user" ]
	list_filter = [ "personal_manager" ]
	ordering = [ "user" ]
	def link_to_user( self, profile ):
		return "<a href=\"%s\">%s</a>" % ( reverse( "admin:auth_user_change", args = [ profile.user.id ] ),
						   profile.user.username )
	def generic_formula( self, profile ):
		return profile.discount( None )[2]
	link_to_user.allow_tags = True
	link_to_user.short_description = _("User")
	generic_formula.allow_tags = True
	generic_formula.short_description = _("Formula")

admin.site.register( PartnerProfile, PartnerProfileAdmin )
admin.site.register( City, CityAdmin )
admin.site.register( PersonalManager, PersonalManagerAdmin )
