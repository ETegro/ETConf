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
from configurator.creator.models import *
from django.utils.translation import ugettext as _

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

class ExpandingAdmin( admin.ModelAdmin ):
	ordering = [ "feature" ]
	list_display = [ "__unicode__" ]

class FeatureAdmin( admin.ModelAdmin ):
	ordering = [ "name" ]

class ComponentGroupAdmin( admin.ModelAdmin ):
	ordering = [ "order" ]
	search_fields = [ "name",
	                  "description",
			  "description_en" ]
	list_display = [ "name",
	                 "subsystem",
			 "equality",
			 "link_move" ]
	list_filter = [ "equality",
	                "subsystem" ]
	fields = [ "name",
	           "description",
		   "description_en",
		   "subsystem",
		   "equality" ]
	def link_move( self, component_group ):
		return "<a href=\"%s\">&uarr;</a>&nbsp;<a href=\"%s\">&darr;</a>" % \
			( reverse( "configurator.creator.views.move_component_group_up", args = [ component_group.id ] ),
			  reverse( "configurator.creator.views.move_component_group_down", args = [ component_group.id ] ) )
	link_move.allow_tags = True
	link_move.short_description = _("Ordering")

class ComponentGroupSubsystemAdmin( admin.ModelAdmin ):
	ordering = [ "order" ]
	search_fields = [ "name",
	                  "description",
	                  "description_en" ]
	list_display = [ "name", "link_move" ]
	fields = [ "name",
	           "description",
	           "description_en",
		   "explanation",
		   "explanation_en" ]
	def link_move( self, subsystem ):
		return "<a href=\"%s\">&uarr;</a>&nbsp;<a href=\"%s\">&darr;</a>" % \
			( reverse( "configurator.creator.views.move_subsystem_up", args = [ subsystem.id ] ),
			  reverse( "configurator.creator.views.move_subsystem_down", args = [ subsystem.id ] ) )
	link_move.allow_tags = True
	link_move.short_description = _("Ordering")

class ComponentAdmin( admin.ModelAdmin ):
	ordering = [ "order" ]
	fields = [ "name",
	           "name_en",
	           "description",
	           "description_en",
		   "price",
		   "is_percentage",
		   "component_group" ]
	search_fields = [ "name", "description" ]
	list_display = [ "name",
			 "component_group",
			 "price",
			 "link_requires",
			 "link_provides",
			 "link_move_clone" ]
	list_filter = [ "component_group" ]
	actions = [ "add_feature" ]

	def link_move_clone( self, component ):
		code = "<a href=\"%s\">&uarr;</a>&nbsp;" % reverse( "configurator.creator.views.move_component_up",
								    args = [ component.id ] )
		code = code + "<a href=\"%s\">&darr;</a>&nbsp;" % reverse( "configurator.creator.views.move_component_down",
									   args = [ component.id ] )
		code = code + "<a href=\"%s\">+</a>" % reverse( "configurator.creator.views.clone_component",
								args = [ component.id ] )
		return code
	link_move_clone.allow_tags = True
	link_move_clone.short_description = _("Ordering/Clone")

	def link_requires( self, component ):
		code = "<ul>"
		for r in [ Requiring.objects.get( component = component, feature = f ) for f in component.requires.all() ]:
			code = code + ("<li><a href=\"%s\">%s x %i</a></li>" % ( \
				reverse( "admin:creator_requiring_change", args = [ r.id ] ),
				r.feature,
				r.quantity ) )
			
		return code + "</ul>"
	link_requires.allow_tags = True
	link_requires.short_description = _("Requirements")

	def link_provides( self, component ):
		code = "<ul>"
		for p in [ Providing.objects.get( component = component, feature = f ) for f in component.provides.all() ]:
			code = code + ("<li><a href=\"%s\">%s x %i</a></li>" % ( \
				reverse( "admin:creator_providing_change", args = [ p.id ] ),
				p.feature,
				p.quantity ) )
		return code + "</ul>"
	link_provides.allow_tags = True
	link_provides.short_description = _("Providings")

	def add_feature( self, request, queryset ):
		selected = request.POST.getlist( admin.ACTION_CHECKBOX_NAME )
		return HttpResponseRedirect( reverse( "configurator.creator.views.features_add" ) + "?ids=%s" % ",".join( selected ) )
	add_feature.short_description = _("Add features")

class ProvidingAdmin( admin.ModelAdmin ):
	ordering = [ "component" ]
	list_display = [ "component", "feature", "quantity" ]
	list_filter = [ "feature" ]

class RequiringAdmin( admin.ModelAdmin ):
	ordering = [ "component" ]
	list_display = [ "component", "feature", "quantity", "parity" ]
	list_filter = [ "feature" ]

class ComputerModelAdmin( admin.ModelAdmin ):
	ordering = [ "name" ]
	list_display = [ "name",
			 "alias",
			 "slogan",
			 "category",
			 "link_clone",
			 "list_specifications" ]
	fields = [ "name",
		   "description",
		   "description_en",
		   "alias",
		   "slogan",
		   "slogan_en",
		   "category",
		   "components",
		   "is_action",
		   "is_active",
		   "url" ]
	list_filter = [ "is_active",
			"is_action" ]
	def link_clone( self, computermodel ):
		return "<a href=\"%s\">+</a>" % ( reverse( "configurator.creator.views.clone_computermodel",
						  args = [ computermodel.id ] ) )
	def list_specifications( self, computermodel ):
		code = "<ul>"
		for s in Specification.objects.select_related().filter( computermodel = computermodel ).order_by( "skey__order" ):
			code = code + "<li><b>%s</b>: %s</li>" % ( unicode( s.skey ), unicode( s.svalue ) )
		return code + "</ul>"
	link_clone.allow_tags = True
	link_clone.short_description = _("Clone")
	list_specifications.allow_tags = True
	list_specifications.short_description = _("Specifications")

class SubstitutionAdmin( admin.ModelAdmin ):
	ordering = [ "source" ]
	list_filter = [ "source", "target" ]

class CurrencyAdmin( admin.ModelAdmin ):
	ordering = [ "name" ]
	list_display = [ "name", "rate", "is_default" ]

class SpecificationKeyAdmin( admin.ModelAdmin ):
	list_display = [ "name",
	                 "is_summary",
			 "link_move" ]
	fields = [ "name",
	           "name_en",
	           "is_summary" ]
	ordering = [ "order" ]
	def link_move( self, skey ):
		return "<a href=\"%s\">&uarr;</a>&nbsp;<a href=\"%s\">&darr;</a>" % \
			( reverse( "configurator.creator.views.move_specification_key_up", args = [ skey.id ] ),
			  reverse( "configurator.creator.views.move_specification_key_down", args = [ skey.id ] ) )
	link_move.allow_tags = True
	link_move.short_description = _("Ordering")

class SpecificationAdmin( admin.ModelAdmin ):
	list_display = [ "skey", "computermodel", "svalue" ]
	list_filter = [ "computermodel" ]
	ordering = [ "skey__order" ]

class CertificateAdmin( admin.ModelAdmin ):
	list_display = [ "label", "url" ]

class ComputerModelCategoryAdmin( admin.ModelAdmin ):
	list_display = [ "label",
			 "prefix",
			 "description" ]

admin.site.register( Feature, FeatureAdmin )
admin.site.register( ComponentGroup, ComponentGroupAdmin )
admin.site.register( ComponentGroupSubsystem, ComponentGroupSubsystemAdmin )
admin.site.register( Component, ComponentAdmin )
admin.site.register( Providing, ProvidingAdmin )
admin.site.register( Requiring, RequiringAdmin )
admin.site.register( ComputerModel, ComputerModelAdmin )
admin.site.register( Substitution, SubstitutionAdmin )
admin.site.register( Currency, CurrencyAdmin )
admin.site.register( SpecificationKey, SpecificationKeyAdmin )
admin.site.register( Specification, SpecificationAdmin )
admin.site.register( Expanding, ExpandingAdmin )
admin.site.register( Certificate, CertificateAdmin )
admin.site.register( ComputerModelCategory, ComputerModelCategoryAdmin )
