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
import configurator.carter.conversions as conversions

import datetime
import re

from django.contrib.auth.models import User
#from configurator.partners.models import PartnerProfile

CurrentCurrency = Currency.objects.get( is_default = True )

def __detect_partner( request ):
	name = re.search( r"^(.*).partners.etegro.com:?.*$",
			  request.META["HTTP_HOST"] )
	if not name: return
	name = name.group(1)
	user = User.objects.filter( username = name )
	if user.count() == 0: return
	return ( name, user[0].email, user[0].get_profile() )

def __render_email( order_request, orders, partner ):
	return render_to_string( "email.txt",
				 { "order_request": order_request,
				   "orders": orders,
				   "partner": partner,
				   "settings": settings } )

def __check_expired_orders():
	for order in Order.objects.filter( created__lte = "%s" % str(datetime.date.today() - datetime.timedelta( days = 5 )) ): order.delete()

def __check_google_conversions( aliases ):
	codes = []
	for target, code in conversions.conversions.iteritems():
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
		response.set_cookie( settings.CART_COOKIE_NAME, cookie_id, path = settings.SESSION_COOKIE_PATH )
	else:
		order = Order( configuration = configuration )
		order.save()
		response.set_cookie( settings.CART_COOKIE_NAME, order.cookie_id, path = settings.SESSION_COOKIE_PATH )
		__check_expired_orders()
	cookie_id = order.cookie_id

	# Delete previous order if there is need in that
	if request.GET.has_key( "previous_order" ) and request.GET["previous_order"]:
		order = Order.objects.filter( cookie_id = cookie_id, id = int( request.GET["previous_order"] ) )
		if order.count() > 0:
			order = order[0]
			order.delete()

	return response

@never_cache
def order_show( request ):
	partner = __detect_partner( request )
	if request.COOKIES.has_key( settings.CART_COOKIE_NAME ):
		cookie_id = request.COOKIES[ settings.CART_COOKIE_NAME ]
	else:
		return render_to_response( "empty.html", { "partner": partner } )
	orders = Order.objects.filter( cookie_id = cookie_id )
	if orders.count() == 0:
		return render_to_response( "empty.html", { "partner": partner } )

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
			body = __render_email( order_request, orders, partner )
			order_request.body = body
			order_request.save()

			if partner:
				send_mail( "%s %s" % ( _("Order %i from") % order_request.id, partner[2].company_name ),
					   body, partner[1], [ partner[1], data["email"] ],
					   fail_silently = False )
				send_mail( "[%s] %i %s %s" % ( _("Order from partner"),
							       order_request.id,
							       _("from "),
							       partner[2].company_name ),
					   body, settings.ORDER_FROM, [ settings.ORDER_CC ],
					   fail_silently = False )
			else:
				send_mail( "%s %s" % ( _("Order %i from") % order_request.id, settings.ORDER_SUBJECT_FROM ),
					   body, settings.ORDER_FROM, [ settings.ORDER_CC, data["email"] ],
					   fail_silently = False )

			response = render_to_response( "successful_submit.html",
						     { "order_request_id": order_request.id,
						       "conversions": __check_google_conversions( set([ o["computer_model"].alias for o in orders ]) ),
						       "partner": partner,
						       "settings": settings } )
			response.delete_cookie( settings.CART_COOKIE_NAME )
			return response
	else:
		form = OrderSubmitForm()
	return render_to_response( "cart.html", {
				   "orders": [ o.get_configuration() for o in orders.order_by( "created" ) ],
				   "cache_timeout": settings.CACHE_TIMEOUT,
			           "partner": partner,
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
