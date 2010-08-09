# -*- coding: utf-8 -*-
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

from configurator.creator.models import *
from configurator.carter.models import *

from configurator.carter.forms import *

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import ugettext as _
from django.views.decorators.cache import *

import configurator.giver.views as giver

import datetime

CurrentCurrency = Currency.objects.get( is_default = True )

def __render_email( order_request, orders ):
	return render_to_string( "email.txt",
				 { "order_request": order_request,
				   "orders": orders,
				   "settings": settings } )

def __check_expired_orders():
	for order in Order.objects.filter( created__lte = "%s" % str(datetime.date.today() - datetime.timedelta( days = 5 )) ): order.delete()

def __check_google_conversions( aliases ):
	# It is an associate array of alias and corresponding
	# conversion's scripts
	conversions = { "dummy": "conversions/dummy.js" }
	codes = []
	for target, code in conversions.iteritems():
		if target in aliases: codes.append( render_to_string( code ) )
	return codes

@never_cache
def order_create( request, computermodel_alias ):
	computermodel = get_object_or_404( ComputerModel, alias = computermodel_alias )
	rendered = giver.render( computermodel, giver.components( request, computermodel ) )
	configuration = { "price": rendered["price"],
			  "currency": rendered["currency"],
			  "configuration": rendered["ids"],
			  "computer_model": rendered["computermodel"] }
	configuration["groups"] = []
	for group in rendered["groups"]:
		components = []
		for component in group["components"]:
			if not component.has_key("quantity"): continue
			if component["quantity"] == 0: continue
			components.append({ "component": component["object"],
					    "quantity": component["quantity"],
					    "price_single": component["price_single"],
					    "price_total": component["price_total"] })
		if len( components ) > 0:
			configuration["groups"].append( ( ComponentGroup.objects.get( name = group["name"] ),
							  components ) )
	response = HttpResponse( reverse( "configurator.carter.views.order_show" ) )

	previous_order_exists = False
	if request.COOKIES.has_key( settings.CART_COOKIE_NAME ):
		cookie_id = request.COOKIES[ settings.CART_COOKIE_NAME ]
		previous_order_exists = Order.objects.filter( cookie_id = cookie_id ).count() != 0

	if previous_order_exists:
		order = Order( configuration = configuration, cookie_id = cookie_id )
		order.save()
		response.set_cookie( settings.CART_COOKIE_NAME, cookie_id )
	else:
		order = Order( configuration = configuration )
		order.save()
		response.set_cookie( settings.CART_COOKIE_NAME, order.cookie_id )
		__check_expired_orders()
	return response

@never_cache
def order_show( request ):
	if request.COOKIES.has_key( settings.CART_COOKIE_NAME ):
		cookie_id = request.COOKIES[ settings.CART_COOKIE_NAME ]
	else:
		return render_to_response( "empty.html" )
	orders = Order.objects.filter( cookie_id = cookie_id )
	if orders.count() == 0:
		return render_to_response( "empty.html" )

	if request.method == "POST":
		form = OrderSubmitForm( request.POST )
		if form.is_valid():
			orders = []
			for order in Order.objects.filter( cookie_id = cookie_id ).order_by( "created" ):
				orders.append( order.get_configuration() )
				order.delete()
			data = form.cleaned_data
			order_request = OrderRequest( company = data["company"],
						      name = data["name"],
						      address = data["address"],
						      email = data["email"],
						      telephone = data["telephone"],
						      comment = data["comment"],
						      price = sum([ o["price"] for o in orders ]),
						      currency = orders[0]["currency"] )
			order_request.save()
			body = __render_email( order_request, orders )
			order_request.body = body
			order_request.save()
			send_mail( "%s %s" % ( _("Order %i from") % order_request.id, settings.ORDER_SUBJECT_FROM ),
				   body,
				   settings.ORDER_FROM,
				   [ settings.ORDER_CC, data["email"] ],
				   fail_silently = False )
			response = render_to_response( "successful_submit.html",
						     { "order_request_id": order_request.id,
						       "conversions": __check_google_conversions( set([ o["computer_model"].alias for o in orders ]) ),
						       "settings": settings } )
			response.delete_cookie( settings.CART_COOKIE_NAME )
			return response
	else:
		form = OrderSubmitForm()
	return render_to_response( "cart.html", {
				   "orders": [ o.get_configuration() for o in orders.order_by( "created" ) ],
				   "cache_timeout": settings.CACHE_TIMEOUT,
				   "form": form,
				   "currency": Order.objects.filter( cookie_id = cookie_id )[0].get_configuration()["currency"],
				   "total_price": sum([ o.get_configuration()["price"] for o in Order.objects.filter( cookie_id = cookie_id ) ]) } )

@never_cache
def order_remove( request, order_id ):
	if Order.objects.filter( id = order_id ).count() > 0:
		order_to_remove = Order.objects.get( id = order_id )
		if request.COOKIES.has_key( settings.CART_COOKIE_NAME ):
			cookie_id = request.COOKIES[ settings.CART_COOKIE_NAME ]
			if order_to_remove.cookie_id == cookie_id:
				order_to_remove.delete()
	return HttpResponseRedirect( reverse( "configurator.carter.views.order_show" ) )
