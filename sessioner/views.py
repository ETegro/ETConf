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

from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

def get_next( request ):
	if request.GET.has_key( "next" ):
		return request.GET["next"]
	else:
		return "http://www.etegro.com/"

def perform_login( request ):
	r = request.GET
	next = get_next( request )

	if request.user.is_authenticated():
		return HttpResponseRedirect( next )

	user = None
	if r.has_key( "username" ) and r.has_key( "password" ):
		user = authenticate( username = r["username"],
				     password = r["password"] )
	if user is not None:
		if user.is_active:
			login( request, user )

	return HttpResponseRedirect( next )

def perform_logout( request ):
	logout( request )
	return HttpResponseRedirect( get_next( request ) )
