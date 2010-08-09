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

import configurator.marketer.servers_urls

from django.template.loader import render_to_string
from django.http import HttpResponse
from django.core.cache import cache

from datetime import datetime

def __yandex_date( date ):
	d = date.timetuple()
	return "%d-%02d-%02d %02d:%02d" % ( d[0], d[1], d[2], d[3], d[4] )

def __picture_url( alias ):
	return "http://www.etegro.com/img/%s/%s/0.jpg" % ( alias[0:2], alias[2:] )

def perform( request ):
	response = cache.get( "yml_response" )
	if response: return response
	offers = []
	for alias, url in configurator.marketer.servers_urls.URLS.iteritems():
		cm = ComputerModel.objects.get( alias = alias )
		offers.append( { "url": "http://www.etegro.com/products/%s" % url,
				 "id": cm.id,
				 "price": int( cm.get_default_price() ),
				 "description": cm.slogan,
				 "model": cm.name,
				 "vendorcode": alias,
				 "picture": __picture_url( alias ),
				 "params": Specification.objects.filter( computermodel = cm ).filter( skey__is_summary__exact = True ).order_by( "skey__order" ).values_list( "skey__name", "svalue" ) } )
	response = HttpResponse( render_to_string( "market.xml",
						 { "date": __yandex_date( datetime.now() ),
						   "offers": offers } ),
				 mimetype = "application/xml" )
				
	cache.add( "yml_response", response )
	return response
