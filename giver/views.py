# -*- coding: utf-8 -*-
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

from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.template import RequestContext

from configurator.giver.forms import *
from configurator.partners.models import PartnerProfile
from django.contrib.auth.models import User

from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import ugettext as _

from configurator.giver.profile import profile

CurrentCurrency = Currency.objects.get( is_default = True )

def __entity_availability( hash, entity ):
	if not hash.has_key( entity ): hash[ entity ] = 0
	return hash

def __component_selections( quantity, parity ):
	return [ i for i in range( parity, quantity+1, parity ) ] or [ 0 ]

def __single_requirement_availability( pool, requirement, quantity = 1, substitutions = False ):
	passed = False
	try:
		cond = pool[ requirement.feature ] >= requirement.quantity * quantity
	except KeyError:
		pool[ requirement.feature ] = 0
		cond = False

	if cond:
		passed = True
	else:
		if not substitutions:
			substitutions = Substitution.objects.select_related( "source" ).filter( target = requirement.feature )
		for s in substitutions:
			try:
				if pool[ requirement.feature ] + pool[ s.source ] >= requirement.quantity * quantity:
					passed = True
			except KeyError:
				continue
				
	if passed:
		return __single_requirement_availability( pool, requirement, quantity + 1, substitutions )
	else:
		return quantity - 1

def component_availability( pool, component, components ):
	requirings = Requiring.objects.filter( component = component ).select_related( "feature" )
	parity = max( [1] + [ r[0] for r in requirings.values_list( "parity" ) ] )
	if requirings.count() == 0: return __component_selections( 1, parity )
	quantity = components.count( component ) + min( [ __single_requirement_availability( pool, r ) for r in requirings ] )

	# Group equality issues
	if component.component_group.equality:
		quantity = quantity + sum([ 1 for c in components if (c.component_group == component.component_group and c != component) ])

	return __component_selections( quantity, parity )

def __validate( components ):
	pool = {}

	# Collect all providings
	for c in components:
		for r in Providing.objects.select_related().filter( component = c ):
			pool = __entity_availability( pool, r.feature )
			pool[ r.feature ] = pool[ r.feature ] + r.quantity

	components = sorted( components,
			     key = lambda c: c.expandings.count(),
			     reverse = True )
	
	# Go through requirings
	for c_id in range( len( components ) ):
		c = components[ c_id ]
		for r in Requiring.objects.select_related().filter( component = c ):
			pool = __entity_availability( pool, r.feature )
			pool[ r.feature ] = pool[ r.feature ] - r.quantity
			if pool[ r.feature ] < 0:
				pool[ r.feature ] = pool[ r.feature ] + r.quantity
				substitution_found = False
				for s in Substitution.objects.select_related().filter( target = r.feature ):
					pool = __entity_availability( pool, s.source )
					pool[ s.source ] = pool[ s.source ] - r.quantity
					if pool[ s.source ] >= 0: substitution_found = True
				if not substitution_found:
					del components[ c_id ]
					return __validate( components )
		for e in Expanding.objects.select_related().filter( component = c ):
			pool = __entity_availability( pool, e.feature )
			if pool[ e.feature ] < e.needed:
				needed_found = False
				for s in Substitution.objects.select_related().filter( target = e.feature ):
					pool = __entity_availability( pool, s.source )
					if pool[ s.source ] >= e.needed: needed_found = True
				if not needed_found: continue
			pool[ e.feature ] = e.quantity
	return ( components, pool )

def render( computermodel, component_ids, quantity = 1, user = None ):
	components = {}
	computermodel_components = computermodel.components.order_by( "order" ).select_related()

	# Parse string and add components available in this model
	for c in computermodel_components: components[ c ] = 0
	for ent in [ [ int(c) for c in p.split("-") ] for p in component_ids.split(",") ]:
		for c in components.keys():
			if c.id == ent[0]:
				components[ c ] = ent[1]
	for c in components.keys():
		if components[ c ] <= 0:
			del components[ c ]
	# Parity checking
	for c in components.keys():
		for r in Requiring.objects.filter( component = c ):
			if components[ c ] % r.parity != 0:
				del components[ c ]
	# Equality checking
	for c in components.keys():
		if c.component_group.equality:
			for cc in components.keys():
				if cc.component_group == c.component_group and cc != c and components.has_key( c ):
					del components[ c ]
	# Flatten components
	components_flattened = []
	[ [ components_flattened.append( c ) for i in range( components[ c ] ) ] for c in components.keys() ]

	components, pool = __validate( components_flattened )
	price_without_percentage = sum([ c.price for c in components if not c.is_percentage ])

	if user:
		calculated_discount = user.discount( computermodel )
	else:
		calculated_discount = None

	# Generating output itself
	price = 0.0
	groups = []
	component_groups = ComponentGroup.objects.select_related().order_by( "order" )
	for cg in component_groups:
		cs = computermodel_components.filter( component_group = cg )
		if cs.count() == 0: continue
		group = { "name": cg.name,
			  "components": [],
			  "input_type": "checkbox" }
		if cg.equality: group["input_type"] = "radio"
		for c in cs:
			entity = { "price_single": int( c.price * CurrentCurrency.rate ),
				   "selections": component_availability( pool, c, components ),
				   "object": c }
			if c.is_percentage:
				entity["price_single"] = int( entity["price_single"] * 0.01 * price_without_percentage )
			if c in components:
				entity["quantity"] = components.count( c )
				entity["price_total"] = entity["price_single"] * entity["quantity"]
				price = price + entity["price_total"]
			if calculated_discount:
				entity["price_single"] = entity["price_single"] * (1 - calculated_discount[0])
				if entity.has_key( "price_total" ):
					entity["price_total"] = entity["price_total"] * (1 - calculated_discount[0])
			if entity["selections"][0] == 0:
				entity["hidden"] = True
			group["components"].append( entity )
		if len( group["components"] ) > 0:
			groups.append( group )

	# Consolidate groups into subsystems
	subsystems = []
	for ss in ComponentGroupSubsystem.objects.order_by( "order" ):
		gs = [ cg for cg in component_groups.filter( subsystem = ss ).order_by( "order" ) \
			if cg.name in [ g["name"] for g in groups ] ]
		if len( gs ) > 0: subsystems.append( ( ss, gs ) )

	# Regenerate configuration string
	ids = {}
	for component in components:
		if not ids.has_key( component.id ): ids[ component.id ] = 0
		ids[ component.id ] = ids[ component.id ] + 1
	component_ids = ",".join( [ "%d-%d" % ( id, q ) for id, q in ids.iteritems() ] )

	if user:
		discount = { "profile": user,
			     "value": int( calculated_discount[0] * 100 ),
			     "price": int( price * (1.0 - calculated_discount[0]) ),
			     "formula": calculated_discount[2] }
		discount["price_quantity"] = discount["price"] * quantity
	else:
		discount = None

	return { "groups": groups,
		 "price": int( price ),
		 "price_quantity": int( price ) * quantity,
		 "discount": discount,
		 "computermodel": computermodel,
		 "ids": component_ids,
		 "subsystems": subsystems,
		 "quantity": quantity,
		 "currency": CurrentCurrency.postfix }
	
def quantity_get( request ):
	if request.GET.has_key( "quantity" ) and request.GET["quantity"]:
		try: return int( request.GET["quantity"] )
		except: pass
	return 1

def components( request, computermodel ):
	if request.GET.has_key( "components" ) and request.GET["components"]:
		return request.GET["components"]
	else:
		return computermodel.get_default_configuration()

def __partner_user( request ):
	user = request.user
	if not user.is_anonymous() and not user.is_superuser:
		try:
			return user.get_profile()
		except:
			return None
	else:
		return None

#@profile( "perform.prof" )
def perform( request, computermodel_alias ):
	computermodel = get_object_or_404( ComputerModel, alias = computermodel_alias )
	if computermodel.components.count() == 0:
		return render_to_response( "computermodel_request.html",
					 { "computermodel": computermodel,
					   "form": ComputerModelRequestForm(),
					   "settings": settings },
					   context_instance=RequestContext(request) )
	return render_to_response( "configurator.html",
				 { "configurator": render( computermodel,
				 			   components( request,
								       computermodel ),
							   quantity = quantity_get( request ),
							   user = __partner_user( request ) ),
				   "cache_timeout": settings.CACHE_MIDDLEWARE_SECONDS },
				   context_instance=RequestContext(request) )

def configurator( request, computermodel_alias ):
	computermodel = get_object_or_404( ComputerModel, alias = computermodel_alias )
	return render_to_response( "initial.html",
				 { "configurator": render( computermodel,
				 			   components( request,
								       computermodel ),
							   quantity = quantity_get( request ),
							   user = __partner_user( request ) ),
				   "cache_timeout": settings.CACHE_MIDDLEWARE_SECONDS,
				   "settings": settings },
				   context_instance=RequestContext(request) )

def __render_computermodel_request_email( computermodel, form ):
	return render_to_string( "computermodel_request_email.txt",
				 { "data": form.cleaned_data,
				   "computermodel": computermodel,
				   "settings": settings } )

def computermodel_request( request, computermodel_alias ):
	computermodel = get_object_or_404( ComputerModel, alias = computermodel_alias )
	form = ComputerModelRequestForm( request.POST )
	if form.is_valid():
		send_mail( "%s %s" % ( _("Request from"), settings.ORDER_SUBJECT_FROM ),
			   __render_computermodel_request_email( computermodel, form ),
			   settings.ORDER_FROM,
			   [ settings.ORDER_CC ],
			   fail_silently = False )
		return render_to_response( "computermodel_request_successful.html",
					 { "computermodel": computermodel,
					   "settings": settings } )
	return render_to_response( "computermodel_request.html",
				 { "form": form,
				   "computermodel": computermodel,
				   "settings": settings } )
