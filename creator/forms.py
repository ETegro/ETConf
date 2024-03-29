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

from django.utils.translation import ugettext as _

class ComponentEditForm( forms.Form ):
	name = forms.CharField( label = _("Name"),
				max_length = 512,
				widget = forms.TextInput( attrs = { "size": "40" } ) )
	description = forms.CharField( label = _("Description"),
				       required = False,
				       widget = forms.Textarea( attrs = { "cols": "80",
				       					  "raws": "20" } ) )
	price = forms.FloatField( label = _("Price") )
	is_percentage = forms.BooleanField( label = _("Percentage"),
					    required = False )

class ComputerModelEditForm( forms.Form ):
	slogan = forms.CharField( label = _("Slogan"),
				  required = False,
				  max_length = 512,
				  widget = forms.TextInput( attrs = { "size": "80" } ) )
	description = forms.CharField( label = _("Description"),
				       required = False,
				       widget = forms.Textarea( attrs = { "cols": "80",
				       					  "raws": "20" } ) )

class FeatureAddForm( forms.Form ):
	feature = forms.ModelChoiceField( queryset = Feature.objects.all(),
					  empty_label = _("Choose feature"),
					  label = _("Feature") )
	type = forms.ChoiceField( label = _("Type"),
				  choices = ( ("providing", _("Providing")),
					      ("requiring", _("Requiring")) ) )
	quantity = forms.IntegerField( label = _("Quantity"),
				       max_value = 100,
				       min_value = 1 )
	parity = forms.IntegerField( label = _("Parity"),
				     required = False )
	def clean_parity( self ):
		data = self.cleaned_data
		parity = data["parity"]
		if data["type"] == "requiring":
			try:
				parity = int( parity )
			except:
				raise forms.ValidationError(_("Enter valid positive integer parity for requiring"))
			if parity <= 0 or parity > 100:
				raise forms.ValidationError(_("Enter valid positive integer parity for requiring"))
		return parity
