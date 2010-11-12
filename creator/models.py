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
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from django.db.models.signals import post_save
import django.dispatch

from configurator.creator.managers import *

from docutils.core import publish_parts

import datetime

DEFAULT_CONFIGURATION_GROUPS = [ "PLATFORM", "CPU", "RAM", "HDD_SATA" ]

class Currency( models.Model ):
	name = models.CharField( _("Name"), max_length = 512 )
	rate = models.FloatField( _("Rate") )
	postfix = models.CharField( _("Postfix"), max_length = 6 )
	is_default = models.BooleanField( _("Default"), default = False )
	def save( self, not_default = False, *args, **kwargs):
		if not not_default:
			for c in Currency.objects.all():
				c.is_default = False
				c.save( not_default = True )
		super( Currency, self ).save(*args, **kwargs)
	def __unicode__( self ):
		return "%s (%s)" % ( self.name, str( self.rate ) )
	class Meta:
		verbose_name = _("Currency")
		verbose_name_plural = _("Currencies")

class Feature( models.Model ):
	name = models.CharField( _("Name"), max_length = 512 )
	description = models.TextField( _("Description"), blank = True )
	def __unicode__( self ):
		return self.name
	class Meta:
		verbose_name = _("Feature")
		verbose_name_plural = _("Features")
		ordering = [ "name" ]

class ComponentGroupSubsystem( models.Model ):
	objects = OrderManager()
	name = models.CharField( _("Name"), max_length = 512 )
	description = models.TextField( _("Description"), blank = True )
	explanation = models.TextField( _("Explanation"), blank = True )
	order = models.PositiveIntegerField( _("Order"), blank = True )
	def __unicode__( self ):
		return self.name
	def save( self, *args, **kwargs):
		if not self.order: self.order = ComponentGroupSubsystem.objects.last_order() + 1
		super( ComponentGroupSubsystem, self ).save(*args, **kwargs)
	class Meta:
		verbose_name = _("Subsystem")
		verbose_name_plural = _("Subsystems")
		ordering = [ "name" ]

class ComponentGroup( models.Model ):
	objects = OrderManager()
	name = models.CharField( _("Name"), max_length = 512 )
	description = models.TextField( _("Description"), blank = True )
	order = models.PositiveIntegerField( _("Order"), blank = True )
	equality = models.BooleanField( _("Equality"), default = False )
	subsystem = models.ForeignKey( ComponentGroupSubsystem,
				       verbose_name = _("Subsystem"),
				       null = True )
	def __unicode__( self ):
		return self.name
	def save( self, *args, **kwargs):
		if not self.order: self.order = ComponentGroup.objects.last_order() + 1
		super( ComponentGroup, self ).save(*args, **kwargs)
	class Meta:
		verbose_name = _("Component group")
		verbose_name_plural = _("Component groups")
		ordering = [ "name" ]

class Component( models.Model ):
	name = models.CharField( _("Name"), max_length = 512 )
	description = models.TextField( _("Description"), blank = True )
	price = models.FloatField( _("Price"), blank = True )
	is_percentage = models.BooleanField( _("Is percentage"), default = False )
	component_group = models.ForeignKey( ComponentGroup,
					     verbose_name = _("Component group") )
	order = models.PositiveIntegerField( _("Order"), blank = True )
	provides = models.ManyToManyField( Feature,
					   related_name = "providings",
					   through = "Providing",
					   verbose_name = _("Provides") )
	requires = models.ManyToManyField( Feature,
					   related_name = "requirings",
					   through = "Requiring",
					   verbose_name = _("Requires") )
	expandings = models.ManyToManyField( Feature,
					     related_name = "expandings",
					     through = "Expanding",
					     verbose_name = _("Expandings") )
	def save( self, not_default = False, *args, **kwargs):
		if not self.order:
			cs = [ c for c in Component.objects.filter( component_group = self.component_group ).order_by( "order" ) ]
			if len( cs ) == 0: self.order = 1
			else: self.order = cs[-1].order + 1
		super( Component, self ).save(*args, **kwargs)
	def __unicode__( self ):
		return self.name
	class Meta:
		verbose_name = _("Component")
		verbose_name_plural = _("Components")
		ordering = [ "name" ]

class Providing( models.Model ):
	component = models.ForeignKey( Component, verbose_name = _("Component") )
	feature = models.ForeignKey( Feature, verbose_name = _("Feature") )
	quantity = models.IntegerField( _("Quantity") )
	def __unicode__( self ):
		return "%s -> %i x %s" % ( unicode( self.component ),
					   self.quantity,
					   unicode( self.feature ) )
	class Meta:
		verbose_name = _("Providing")
		verbose_name_plural = _("Providings")
		ordering = [ "component" ]

class Requiring( models.Model ):
	component = models.ForeignKey( Component, verbose_name = _("Component") )
	feature = models.ForeignKey( Feature, verbose_name = _("Feature") )
	quantity = models.IntegerField( _("Quantity") )
	parity = models.IntegerField( _("Parity"), default = 1 )
	def __unicode__( self ):
		return "%s -> %i x %s [ %i ]" % ( unicode( self.component ),
						  self.quantity,
						  unicode( self.feature ),
						  self.parity )
	class Meta:
		verbose_name = _("Requiring")
		verbose_name_plural = _("Requirings")
		ordering = [ "component" ]

class Expanding( models.Model ):
	component = models.ForeignKey( Component, verbose_name = _("Component") )
	feature = models.ForeignKey( Feature, verbose_name = _("Feature") )
	needed = models.IntegerField( _("Needed") )
	quantity = models.IntegerField( _("Quantity") )
	def __unicode__( self ):
		return "%d x %s -> %d" % ( self.needed,
					   unicode( self.feature ),
					   self.quantity )
	class Meta:
		verbose_name = _("Expanding")
		verbose_name_plural = _("Expandings")
		ordering = [ "component" ]

class SpecificationKey( models.Model ):
	objects = OrderManager()
	name = models.CharField( _("Key name"), max_length = 512 )
	order = models.PositiveIntegerField( _("Order"), blank = True )
	is_summary = models.BooleanField( _("Is summary"), default = False )
	def __unicode__( self ):
		return unicode( self.name )
	def save( self, *args, **kwargs):
		if not self.order: self.order = SpecificationKey.objects.last_order() + 1
		super( SpecificationKey, self ).save(*args, **kwargs)
	class Meta:
		verbose_name = _("Specification key")
		verbose_name_plural = _("Specification keys")
		ordering = [ "name" ]

class ComputerModel( models.Model ):
	name = models.CharField( _("Name"), max_length = 512 )
	description = models.TextField( _("Description"), blank = True )
	description_html = models.TextField( blank = True )
	components = models.ManyToManyField( Component,
					     verbose_name = _("Components"),
					     null = True,
					     blank = True )
	alias = models.CharField( _("Alias"), max_length = 64 )
	is_action = models.BooleanField( _("Is action"),
					 default = False )
	is_active = models.BooleanField( _("Is active"),
					 default = False )
	url = models.CharField( _("Website URL"),
				max_length = 512,
				blank = True,
				null = True )
	default_price = models.FloatField( blank = True, null = True )
	slogan = models.CharField( _("Slogan"),
				   max_length = 512,
				   blank = True,
				   null = True )
	short_configuration_str = models.CharField( _("Short configuration"),
						    max_length = 512,
						    blank = True,
						    null = True )
	support = models.TextField( _("Support"),
				    blank = True,
				    null = True )
	specifications = models.ManyToManyField( SpecificationKey, through = "Specification" )
	last_modified = models.DateTimeField( blank = True,
					      null = True )
	def default_components( self ):
		result = {}
		for group in DEFAULT_CONFIGURATION_GROUPS:
			components = self.components.filter( component_group__name = group ).order_by( "order" ).order_by( "price" )
			if components.count() == 0: continue
			component = components[0]
			quantity = max([1] + [ p[0] for p in Requiring.objects.filter( component = component ).values_list( "parity" ) ])
			result[ component ] = quantity
		for c in self.components.filter( price = 0.0 ): result[ c ] = 1
		return result
	def get_default_configuration( self ):
		return ",".join( [ "%d-%d" % ( c.id, q ) for c, q in self.default_components().iteritems() ] )
	def get_default_price( self ):
		if Currency.objects.filter( is_default = True ).count() == 0: return
		return sum([ c.price * q for c, q in self.default_components().iteritems() ]) * \
				Currency.objects.get( is_default = True ).rate
	def short_configuration( self ):
		configuration = []
		for c, q in self.default_components().iteritems():
			if c.component_group.name == "PLATFORM" or c.price == 0.0: continue
			c = unicode(c).replace(" / ","/")
			if q == 1: configuration.append( c )
			else: configuration.append( "%d x %s" % ( q, c ) )
		return " / ".join( configuration )
	def __url_for( self ):
		if self.url: return "http://www.etegro.com/%s" % self.url
		else: return "http://www.etegro.com/"
	def __buy_url_for( self ):
		return "%s/buy" % self.__url_for()
	def get_url( self ):
		return ( self.__url_for(), { "buy": self.__buy_url_for() } )
	def save( self, *args, **kwargs ):
		if self.id: self.default_price = self.get_default_price()
		self.description_html = publish_parts( self.description, writer_name="html4css1" )["fragment"]
		self.last_modified = datetime.datetime.now()
		self.short_configuration_str = self.short_configuration()
		super( ComputerModel, self ).save(*args, **kwargs)
	def __unicode__( self ):
		return self.name
	class Meta:
		verbose_name = _("Computer model")
		verbose_name_plural = _("Computer models")
		ordering = [ "name" ]

class Specification( models.Model ):
	computermodel = models.ForeignKey( ComputerModel, verbose_name = _("Computer model") )
	skey = models.ForeignKey( SpecificationKey, verbose_name = _("Specification key") )
	svalue = models.TextField( _("Value") )
	def __unicode__( self ):
		return "[%s] %s: %s" % ( unicode( self.computermodel ),
					 unicode( self.skey ),
					 unicode( self.svalue ) )
	class Meta:
		verbose_name = _("Specification")
		verbose_name_plural = _("Specifications")

class Substitution( models.Model ):
	source = models.ForeignKey( Feature,
				    verbose_name = _("Source"),
				    related_name = "sources" )
	target = models.ForeignKey( Feature,
				    verbose_name = _("Target"),
				    related_name = "targets" )
	def __unicode__( self ):
		return "%s -> %s" % ( self.source, self.target )
	class Meta:
		verbose_name = _("Substitution")
		verbose_name_plural = _("Substitutions")


################################################################################
# Signals
################################################################################
def component_save_handler( sender, instance, **kwargs ):
	for cm in ComputerModel.objects.all():
		if not instance in cm.components.all(): continue
		cm.save()
post_save.connect( component_save_handler, sender = Component )

def currency_change_handler( sender, **kwargs ):
	for cm in ComputerModel.objects.all():
		cm.save()
post_save.connect( currency_change_handler, sender = Currency )
