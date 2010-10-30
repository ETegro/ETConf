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

from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
import django.dispatch

from django.utils.translation import ugettext as _

class City( models.Model ):
	name = models.CharField( _("City"), max_length = 512 )
	def __unicode__( self ):
		return self.name
	class Meta:
		verbose_name = _("City")
		verbose_name_plural = _("Cities")
class PersonalManager( models.Model ):
	name = models.CharField( _("Name"), max_length = 512 )
	def __unicode__( self ):
		return self.name
	class Meta:
		verbose_name = _("Personal manager")
		verbose_name_plural = _("Personal managers")

class PartnerProfile( models.Model ):
	user = models.OneToOneField( User, verbose_name = _("User") )
	company_name = models.CharField( _("Company name"),
				     blank = True,
				     max_length = 512 )
	signature = models.TextField( _("Signature"),
				      blank = True )
	city = models.ForeignKey( City,
				  verbose_name = _("City"),
				  blank = True,
				  null = True )
	personal_manager = models.ForeignKey( PersonalManager,
					      verbose_name = _("Personal manager"),
					      blank = True,
					      null = True )
	debt = models.FloatField( _("Debt"), default = 0.0 )
	discount_standart = models.FloatField( _("Discount standart"), default = 0.0 )
	discount_marketing = models.FloatField( _("Discount marketing"), default = 0.0 )
	discount_action = models.FloatField( _("Action discount"), default = 0.0 )
	def __formula( self, dict ):
		return " + ".join( [ "%i%% (%s)" % ( v, unicode(what) ) for what, v in dict.iteritems() ] )
	def discount( self, computer_model ):
		try:
			if computer_model.is_action:
				dict = { _("auction"): self.discount_action }
				return ( float( self.discount_action ) * 0.01,
					 dict,
					 self.__formula( dict ) )
		except: pass
		dict = { _("standart"): self.discount_standart,
			 _("marketing"): self.discount_marketing }
		return ( float( self.discount_standart + self.discount_marketing ) * 0.01,
			 dict,
			 self.__formula( dict ) )
	def __unicode__( self ):
		return "%s (%s)" % ( self.user, self.company_name )
	class Meta:
		verbose_name = _("Partner profile")
		verbose_name_plural = _("Partner profiles")

# Automatic profile creation causes many problems with dump and load
#def user_profile_create( sender, instance, created, **kwargs ):
#	if not created: return
#	if PartnerProfile.objects.filter( user = instance ).count() != 0: return
#	profile = PartnerProfile( user = instance )
#	profile.save()
#post_save.connect( user_profile_create, sender = User )
