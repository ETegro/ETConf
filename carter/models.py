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

from django.db import models
from django.utils.translation import ugettext_lazy as _

import random
import hashlib
import datetime

import cPickle as pickle
from base64 import b64encode, b64decode

class Order( models.Model ):
	cookie_id = models.CharField( max_length = 40 )
	configuration = models.TextField()
	created = models.DateTimeField()
	def get_configuration( self ):
		data = pickle.loads( str( b64decode( self.configuration ) ) )
		data["id"] = self.id
		return data
	def save( self, *args, **kwargs ):
		if not self.cookie_id:
			self.cookie_id = hashlib.sha1( str( random.random() ) ).hexdigest()
		if not self.created:
			self.created = datetime.datetime.now()
		self.configuration = b64encode( pickle.dumps( self.configuration ) )
		super( Order, self ).save(*args, **kwargs)

class OrderRequest( models.Model ):
	company = models.CharField( _("Company"), max_length = 512, blank = True )
	name = models.CharField( _("Name"), max_length = 512 )
	address = models.TextField( _("Delivery address"), blank = True )
	email = models.EmailField( _("Email") )
	telephone = models.CharField( _("Contact telephone"), max_length = 512 )
	comment = models.TextField( _("Comment"), blank = True )
	body = models.TextField( _("Body"), blank = True )
	price = models.FloatField( _("Price"), blank = True )
	currency = models.CharField( _("Currency"), max_length = 512 )
	created = models.DateTimeField()
	def save( self, *args, **kwargs ):
		if not self.created: self.created = datetime.datetime.now()
		super( OrderRequest, self ).save(*args, **kwargs)
	class Meta:
		verbose_name = _("OrderRequest")
		verbose_name_plural = _("OrderRequests")
