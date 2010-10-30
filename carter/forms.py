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

from django import forms

from configurator.creator.models import *
from configurator.carter.models import *

from django.utils.translation import ugettext as _

class OrderSubmitForm( forms.Form ):
	company = forms.CharField( label = _("Company"), required = False )
	name = forms.CharField( label = _("Your name") )
	address = forms.CharField( label = _("Delivery address"),
				   widget = forms.Textarea( attrs = { "cols": "40",
				   				      "rows": "5" } ),
				   required = False )
	email = forms.EmailField( label = _("Your email") )
	telephone = forms.CharField( label = _("Contact telephone") )
	comment = forms.CharField( label = _("Comment"),
				   widget = forms.Textarea( attrs = { "cols": "40",
				   				      "rows": "5" } ),
				   required = False )
