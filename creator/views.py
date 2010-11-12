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

from configurator.creator.models import *
from configurator.creator.forms import *
from django.db.models import Q

from django.utils.translation import ugettext as _

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

from django.conf import settings
from django.core.cache import cache
from django.views.decorators.cache import *
from django.contrib.auth.decorators import login_required, user_passes_test

import re
import subprocess

is_superuser = lambda user: user.is_superuser

def __reverse_admin( postfix ):
	return "%s%s" % ( reverse( "admin:app_list", args = [ "creator" ] ), postfix )

@user_passes_test( is_superuser )
def move_component_up( request, component_id ):
	component = get_object_or_404( Component, id = component_id )
	gc = [ c for c in Component.objects.filter( component_group = component.component_group ).order_by( "order" ) ]
	if gc.index( component ) != 0:
		previous = gc[ gc.index( component ) - 1 ]
		previous.order = previous.order + 1
		component.order = component.order - 1
		previous.save()
		component.save()
	return HttpResponseRedirect( __reverse_admin( "component/?component_group__id__exact=%d" % component.component_group.id ) )

@user_passes_test( is_superuser )
def move_component_down( request, component_id ):
	component = get_object_or_404( Component, id = component_id )
	gc = [ c for c in Component.objects.filter( component_group = component.component_group ).order_by( "order" ) ]
	if gc[-1] != component:
		previous = gc[ gc.index( component ) + 1 ]
		previous.order = previous.order - 1
		component.order = component.order + 1
		previous.save()
		component.save()
	return HttpResponseRedirect( __reverse_admin( "component/?component_group__id__exact=%d" % component.component_group.id ) )

@user_passes_test( is_superuser )
def clone_component( request, component_id ):
	component = get_object_or_404( Component, id = component_id )
	neu = Component( name = "%s %s" % ( component.name, _("Clone") ),
			 description = component.description,
			 price = component.price,
			 is_percentage = component.is_percentage,
			 component_group = component.component_group,
			 order = Component.objects.filter( component_group = component.component_group ).count() )
	neu.save()
	for p in Providing.objects.filter( component = component ):
		neu_p = Providing( component = neu,
				   feature = p.feature,
				   quantity = p.quantity )
		neu_p.save()
	for r in Requiring.objects.filter( component = component ):
		neu_r = Requiring( component = neu,
				   feature = r.feature,
				   quantity = r.quantity,
				   parity = r.parity )
		neu_r.save()
	return HttpResponseRedirect( reverse( "admin:creator_component_change", args = [ neu.id ] ) )

@user_passes_test( is_superuser )
def clone_computermodel( request, computermodel_id ):
	computermodel = get_object_or_404( ComputerModel, id = computermodel_id )
	neu = ComputerModel( name = "%s %s" % ( computermodel.name, _("Clone") ),
			     description = computermodel.description,
			     alias = "%s-clone" % computermodel.alias,
			     default_price = computermodel.default_price,
			     slogan = computermodel.slogan )
	neu.save()
	for c in computermodel.components.all(): neu.components.add( c )
	return HttpResponseRedirect( reverse( "admin:creator_computermodel_change", args = [ neu.id ] ) )

def __render_rst( computermodel ):
	cm = computermodel
	header_lines = lambda h, s: "".join( [ s for i in range( len( h ) ) ] )
	splitted_alias = re.search( r"^(..)(.*)$", cm.alias )
	return render_to_string( "computermodel.rst",
			 { "main_header": "%s\n%s\n%s" % ( header_lines( cm.name, "=" ),
							   cm.name,
							   header_lines( cm.name, "=" ) ),
			   "slogan": cm.slogan,
			   "description": cm.description,
			   "images_path": settings.IMAGES_PATH,
			   "main_image": ( splitted_alias.group(1),
			   		   splitted_alias.group(2) ),
			   "specifications": [ { "skey": s.skey.name,
			   			 "svalues": s.svalue.replace( "\r\n", "\n" ).split( "\n" ) }
					for s in Specification.objects.select_related().filter( computermodel = cm ).order_by( "skey__order" ) ] } )

def render_rst( request, computermodel_alias ):
	cm = get_object_or_404( ComputerModel, alias = computermodel_alias )
	response = HttpResponse( __render_rst( cm ), mimetype = "text/x-rst" )
	response["Content-Disposition"] = "attachment; filename=%s.rst" % computermodel_alias
	return response 

def render_pdf( request, computermodel_alias ):
	response = cache.get( "%s.pdf" % computermodel_alias )
	if response: return response
	cm = get_object_or_404( ComputerModel, alias = computermodel_alias )
	renderer = subprocess.Popen( [ "rst2pdf",
				       "--font-path=%s" % settings.FONTS_PATH,
				       "--stylesheets=%s" % settings.STYLE_PATH ],
				     close_fds = True,
				     stdin = subprocess.PIPE,
				     stdout = subprocess.PIPE )
	response = HttpResponse( renderer.communicate( input =  __render_rst( cm ).encode("utf8") )[0],
				 mimetype = "application/pdf" )
	response["Content-Disposition"] = "attachment; filename=%s.pdf" % computermodel_alias
	cache.add( "%s.pdf" % computermodel_alias, response )
	return response

def __change_order( modelname, object, iterator ):
	entities = list( modelname.objects.all().order_by( "order" ).values_list( "id", "order" ) )
	index_of = entities.index( (object.id, object.order) )
	previous = modelname.objects.get( id = entities[ iterator( index_of ) ][0] )
	object.order = entities[ iterator( index_of ) ][1]
	object.save()
	previous.order = entities[ index_of ][1]
	previous.save()

def __change_order_up( modelname, object ):
	if object.order == 1: return
	__change_order( modelname, object, lambda x: x - 1 )

def __change_order_down( modelname, object ):
	if object.order == modelname.objects.last_order(): return
	__change_order( modelname, object, lambda x: x + 1 )

@user_passes_test( is_superuser )
def move_specification_key_up( request, specification_key_id ):
	skey = get_object_or_404( SpecificationKey, id = specification_key_id )
	__change_order_up( SpecificationKey, skey )
	return HttpResponseRedirect( __reverse_admin( "specificationkey" ) )

@user_passes_test( is_superuser )
def move_specification_key_down( request, specification_key_id ):
	skey = get_object_or_404( SpecificationKey, id = specification_key_id )
	__change_order_down( SpecificationKey, skey )
	return HttpResponseRedirect( __reverse_admin( "specificationkey" ) )

@user_passes_test( is_superuser )
def move_component_group_up( request, component_group_id ):
	component_group = get_object_or_404( ComponentGroup, id = component_group_id )
	__change_order_up( ComponentGroup, component_group )
	return HttpResponseRedirect( __reverse_admin( "componentgroup" ) )

@user_passes_test( is_superuser )
def move_component_group_down( request, component_group_id ):
	component_group = get_object_or_404( ComponentGroup, id = component_group_id )
	__change_order_down( ComponentGroup, component_group )
	return HttpResponseRedirect( __reverse_admin( "componentgroup" ) )

@user_passes_test( is_superuser )
def move_subsystem_up( request, subsystem_id ):
	subsystem = get_object_or_404( ComponentGroupSubsystem, id = subsystem_id )
	__change_order_up( ComponentGroupSubsystem, subsystem )
	return HttpResponseRedirect( __reverse_admin( "componentgroupsubsystem" ) )

@user_passes_test( is_superuser )
def move_subsystem_down( request, subsystem_id ):
	subsystem = get_object_or_404( ComponentGroupSubsystem, id = subsystem_id )
	__change_order_down( ComponentGroupSubsystem, subsystem )
	return HttpResponseRedirect( __reverse_admin( "componentgroupsubsystem" ) )

@user_passes_test( is_superuser )
def specifications_clone( request, computermodel_src_alias, computermodel_dst_alias ):
	src = get_object_or_404( ComputerModel, alias = computermodel_src_alias )
	dst = get_object_or_404( ComputerModel, alias = computermodel_dst_alias )
	for spec in Specification.objects.filter( computermodel = src ):
		neu = Specification( computermodel = dst,
				     skey = spec.skey,
				     svalue = spec.svalue )
		neu.save()
	return HttpResponseRedirect( __reverse_admin( "computermodel" ) )

def __computermodel_components( computermodel ):
	included = Q()
	for c in computermodel.components.all(): included = included | Q( id = c.id )
	return included

@never_cache
@user_passes_test( is_superuser )
def components_editor( request, computermodel_alias ):
	cm = get_object_or_404( ComputerModel, alias = computermodel_alias )
	if request.method == "POST":
		ids = [ int(id) for id in request.POST["ids"].split(",") if id ]
		current = [ id[0] for id in Component.objects.filter( __computermodel_components( cm ) ).values_list( "id" ) ]
		[ cm.components.add( Component.objects.get( id = id ) ) for id in ids if not id in current ]
		[ cm.components.remove( Component.objects.get( id = id ) ) for id in current if not id in ids ]
		return HttpResponse( reverse( "configurator.creator.views.components_editor", args = [ cm.alias ] ) )

	components = Component.objects.all()
	groups = []

	if cm.components.all().count() == 0:
		for cg in ComponentGroup.objects.all().order_by( "order" ):
			group_available = components.filter( component_group = cg ).order_by( "order" )
			if group_available.count() == 0: continue
			groups.append( { "group": cg,
					 "available": group_available,
					 "included": [] } )
	else:
		included_query = __computermodel_components( cm )
		available = components.exclude( included_query )
		included = components.filter( included_query )
		for cg in ComponentGroup.objects.all().order_by( "order" ):
			group_available = available.filter( component_group = cg ).order_by( "order" )
			group_included = included.filter( component_group = cg ).order_by( "order" )
			if group_available.count() == 0 and group_included.count() == 0: continue
			groups.append( { "group": cg,
					 "available": group_available,
					 "included": group_included } )

	return render_to_response( "components_editor.html",
				 { "groups": groups,
				   "computermodel": cm,
				   "computermodels": ComputerModel.objects.all().order_by( "name" ),
				   "specifications": Specification.objects.filter( computermodel = cm ),
				   "specification_keys": SpecificationKey.objects.all().order_by( "order" ),
				   "settings": settings,
				   "form": ComputerModelEditForm( { "slogan": cm.slogan,
				   				    "description": cm.description } ) } )

@never_cache
@user_passes_test( is_superuser )
def component_edit( request ):
	r = request.POST
	component = get_object_or_404( Component, id = r["component_id"] )
	auto_id = "%i_%%s" % component.id
	if r.has_key("name"):
		form = ComponentEditForm( r, auto_id = auto_id )
		if form.is_valid():
			data = form.cleaned_data
			component.name = data["name"]
			component.description = data["description"]
			component.price = data["price"]
			if r["is_percentage"] == "true":
				component.is_percentage = True
			else:
				component.is_percentage = False
			component.save()
			return HttpResponse("saved")
	else:
		form = ComponentEditForm( { "name": component.name,
					    "description": component.description,
					    "price": component.price,
					    "is_percentage": component.is_percentage },
					  auto_id = auto_id )
	return render_to_response( "component_edit.html",
				 { "form": form,
				   "component": component } )

@never_cache
@user_passes_test( is_superuser )
def specification_edit( request, computermodel_alias ):
	computermodel = get_object_or_404( ComputerModel, alias = computermodel_alias )
	r = request.POST
	for specification_key_id, svalue in r.iteritems():
		specification_key = SpecificationKey.objects.get( id = specification_key_id )
		if svalue == "":
			specification = Specification.objects.filter( skey = specification_key, computermodel = computermodel )
			if specification.count() != 0: specification[0].delete()
			continue
		specification = Specification.objects.get_or_create( computermodel = computermodel,
								     skey = specification_key )[0]
		specification.svalue = svalue
		specification.save()
	return render_to_response( "specification_editor_page.html",
				   { "specifications": Specification.objects.filter( computermodel = computermodel ),
				     "specification_keys": SpecificationKey.objects.all().order_by( "order" ),
				     "computermodel": computermodel } )

@never_cache
@user_passes_test( is_superuser )
def computermodel_edit( request, computermodel_alias ):
	pass
	r = request.POST
	cm = get_object_or_404( ComputerModel, alias = computermodel_alias )
	form = ComputerModelEditForm( r )
	message = ""
	if form.is_valid():
		data = form.cleaned_data
		cm.slogan = data["slogan"]
		cm.description = data["description"]
		cm.save()
		message = _("Computer model updated")
	return render_to_response( "computermodel_editor_page.html",
				   { "computermodel": cm,
				     "message": message,
				     "form": form } )

@never_cache
@user_passes_test( is_superuser )
def features_add( request ):
	if request.GET.has_key("ids"):
		ids = request.GET["ids"]
	else:
		ids = request.POST["ids"]

	query = Q()
	for id in [ int( id ) for id in ids.split(",") ]:
		query = query | Q( id = id )
	components = Component.objects.filter( query )

	if request.GET.has_key("ids"):
		ids = request.GET["ids"]
		form = FeatureAddForm()
	else:
		ids = request.POST["ids"]
		form = FeatureAddForm( request.POST )
		if form.is_valid():
			data = form.cleaned_data
			for component in components.all():
				if data["type"] == "providing":
					providing = Providing.objects.get_or_create( component = component,
										     quantity = data["quantity"],
										     feature = data["feature"] )
				else:
					requiring = Requiring.objects.get_or_create( component = component,
										     quantity = data["quantity"],
										     feature = data["feature"],
										     parity = data["parity"] )
			return HttpResponseRedirect( __reverse_admin( "component" ) )
	return render_to_response( "features_add.html",
				 { "ids": ids,
				   "form": form,
				   "components": components } )
