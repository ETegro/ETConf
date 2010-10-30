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
from configurator.giver.views import *

from django.test import TestCase

def genids( ids ):
	to_join = []
	for component, quantity in ids.iteritems():
		to_join.append( "%d-%d" % ( component.id, quantity ) )
	return ",".join( to_join )

class BasicRenderTest( TestCase ):
	fixtures = [ "test_giver" ]
	def setUp( self ):
		self.computer_model = ComputerModel.objects.get( id = 1 )
	def test_rsbase( self ):
		self.assertEqual( render( self.computer_model, "11-1" )["price"], 100.0 )
	def test_one_component( self ):
		self.assertEqual( render( self.computer_model, "11-1,1-1" )["price"], 100.0 + 45.0 )
	def test_double_component( self ):
		self.assertEqual( render( self.computer_model, "11-1,1-2" )["price"], 100.0 + 45.0 * 2 )
	def test_unexistent_id( self ):
		self.assertEqual( render( self.computer_model, "12-1" )["price"], 0.0 )
	def test_not_enough_resources( self ):
		self.assertEqual( render( self.computer_model, "11-1,1-3" )["price"], 100.0 + 45.0 * 2 )
	def test_parity( self ):
		self.assertEqual( render( self.computer_model, "11-1,4-3" )["price"], 100.0 )
		self.assertEqual( render( self.computer_model, "11-1,4-1" )["price"], 100.0 )

class ComplexRenderTest( TestCase ):
	fixtures = [ "test_giver" ]
	def setUp( self ):
		self.computer_model = ComputerModel.objects.get( id = 1 )
		self.correct = []
		self.correct.append( {"input_type": "radio", "name": u"PLATFORM", "components": []} )
		self.correct[-1]["components"].append( {"price_single": 100.0,
							"price_total": 100.0,
							"quantity": 1,
							"object": Component.objects.get( name = "RSbase" ),
							"selections": [1]} )
		self.correct.append( {"input_type": "radio", "name": u"CPU", "components": []} )
		self.correct[-1]["components"].append( {"price_single": 25.0,
							"object": Component.objects.get( name = "Core2" ),
							"selections": [1,2]} )
		self.correct[-1]["components"].append( {"price_single": 45.0,
							"object": Component.objects.get( name = "Opteron" ),
							"selections": [1,2]} )
		self.correct.append( {"input_type": "checkbox", "name": u"RAM", "components": []} )
		self.correct[-1]["components"].append( {"price_single": 20.0,
							"object": Component.objects.get( name = "Four GB" ),
							"selections": [2,4]} )
		self.correct[-1]["components"].append( {"price_single": 15.0,
							"object": Component.objects.get( name = "Two GB" ),
							"selections": [1,2,3,4]} )
		self.correct.append( {"input_type": "checkbox", "name": u"HDD", "components": []} )
		self.correct[-1]["components"].append( {"price_single": 40.0,
							"object": Component.objects.get( name = "GB250B" ),
							"selections": [1,2]} )
		self.correct[-1]["components"].append( {"price_single": 40.0,
							"object": Component.objects.get( name = "GB250S" ),
							"hidden": True,
							"selections": [0]} )
		self.correct[-1]["components"].append( {"price_single": 10.0,
							"object": Component.objects.get( name = "Kit2535" ),
							"selections": [1]} )
		self.correct[-1]["components"].append( {"price_single": 40.0,
							"object": Component.objects.get( name = "WD350B" ),
							"selections": [1,2]} )
		self.correct[-1]["components"].append( {"price_single": 40.0,
							"object": Component.objects.get( name = "WD350S" ),
							"hidden": True,
							"selections": [0]} )
		self.correct.append( {"input_type": "checkbox", "name": u"CTRL", "components": []} )
		self.correct[-1]["components"].append( {"price_single": 50.0,
							"object": Component.objects.get( name = "MegaRAID" ),
							"selections": [1,2]} )

	def test_empty( self ):
		self.assertEqual( render( self.computer_model, "11-1" )["groups"][0], self.correct[0] )
		self.assertEqual( render( self.computer_model, "11-1" )["groups"][1], self.correct[1] )
		self.assertEqual( render( self.computer_model, "11-1" )["groups"][2], self.correct[2] )
		self.assertEqual( render( self.computer_model, "11-1" )["groups"][3], self.correct[3] )
		self.assertEqual( render( self.computer_model, "11-1" )["groups"][4], self.correct[4] )
		self.assertEqual( render( self.computer_model, "11-1" )["price"], 100.0 )

	def test_add_one_cpu( self ):
		self.correct[1]["components"][0]["quantity"] = 1
		self.correct[1]["components"][0]["price_total"] = self.correct[1]["components"][0]["price_single"]
		self.correct[1]["components"][1]["selections"] = [1,2]
		self.assertEqual( render( self.computer_model, "11-1,2-1" )["groups"][1], self.correct[1] )
		self.assertEqual( render( self.computer_model, "11-1,2-1" )["price"], 100.0 + 25.0 )
	
	def test_add_enclosure_kit( self ):
		self.correct[3]["components"][2]["quantity"] = 1
		self.correct[3]["components"][2]["price_total"] = self.correct[3]["components"][2]["price_single"]
		self.correct[3]["components"][0]["hidden"] = True
		self.correct[3]["components"][0]["selections"] = [1,2,3]
		del self.correct[3]["components"][1]["hidden"]
		self.correct[3]["components"][1]["selections"] = [1,2,3]
		self.correct[3]["components"][3]["hidden"] = True
		self.correct[3]["components"][3]["selections"] = [0]
		del self.correct[3]["components"][4]["hidden"]
		self.correct[3]["components"][4]["selections"] = [1,2,3]
		self.assertEqual( render( self.computer_model, "11-1,9-1" )["groups"][1], self.correct[1] )
		self.assertEqual( render( self.computer_model, "11-1,9-1" )["price"], 100.0 + 10.0 )
	
	def test_add_doubled_memory_with_controller( self ):
		self.correct[2]["components"][0]["quantity"] = 2
		self.correct[2]["components"][0]["price_total"] = self.correct[2]["components"][0]["price_single"] * 2
		self.correct[2]["components"][1]["selections"] = [1,2]
		self.correct[4]["components"][0]["quantity"] = 1
		self.correct[4]["components"][0]["price_total"] = self.correct[4]["components"][0]["price_single"]
		self.assertEqual( render( self.computer_model, "11-1,10-1,4-2" )["groups"][1], self.correct[1] )
		self.assertEqual( render( self.computer_model, "11-1,10-1,4-2" )["price"], 100.0 + 2*20.0 + 50.0 )

class SubstitutionTest( TestCase ):
	fixtures = [ "test_giver" ]
	def setUp( self ):
		self.computer_model = ComputerModel.objects.get( id = 1 )
		substitution = Substitution( source = Feature.objects.get( name = "SAS" ),
					    target = Feature.objects.get( name = "SATA" ) )
		substitution.save()
		# Let RSbase will provide only two SATA ports
		p = Providing.objects.get( component = Component.objects.get( name = "RSbase" ),
					   feature = Feature.objects.get( name = "SATA" ) )
		p.quantity = 2
		p.save()
		# Let RSbase will provide four 2.5 enclosures
		p = Providing.objects.get( component = Component.objects.get( name = "RSbase" ),
					   feature = Feature.objects.get( name = "Enclosure35" ) )
		p.quantity = 4
		p.save()
		# And HDD of course needs SATA port that is not mentioned in database
		p = Requiring( component = Component.objects.get( name = "WD350B" ),
			       feature = Feature.objects.get( name = "SATA" ),
			       quantity = 1 )
		p.save()
		# Client request emulation
		self.ids = ",".join( [ "%i-%i" % ( Component.objects.get( name = "RSbase" ).id, 1 ),
				       "%i-%i" % ( Component.objects.get( name = "MegaRAID" ).id, 1 ),
				       "%i-%i" % ( Component.objects.get( name = "WD350B" ).id, 4 ) ] )
	def test_with_controller( self ):
		self.assertEqual( render( self.computer_model, self.ids )["groups"][3]["components"][3]["quantity"], 4 )
	def test_without_controller( self ):
		self.assertEqual( render( self.computer_model,
					  self.ids.replace( "10-1,", "" ) )["groups"][3]["components"][3]["quantity"], 2 )

class AvailabilityTest( TestCase ):
	fixtures = [ "test_giver" ]
	def setUp( self ):
		self.kit23 = Feature( name = "kit23" )
		self.kit23.save()
		self.kit2 = Feature.objects.get( name = "Enclosure25" )
		self.kit3 = Feature.objects.get( name = "Enclosure35" )
		self.subst1 = Substitution( source = self.kit23, target = self.kit2 )
		self.subst2 = Substitution( source = self.kit23, target = self.kit3 )
		self.subst1.save()
		self.subst2.save()
		self.hdd1 = Component.objects.get( name = "GB250S" )
		self.hdd2 = Component.objects.get( name = "GB250B" )
	def test_double_enclosures( self ):
		pool = { self.kit2: 4 }
		self.assertEqual( component_availability( pool, self.hdd1, [] ), [1,2,3,4] )
		self.assertEqual( component_availability( pool, self.hdd2, [] ), [0] )

		pool = { self.kit3: 4 }
		self.assertEqual( component_availability( pool, self.hdd1, [] ), [0] )
		self.assertEqual( component_availability( pool, self.hdd2, [] ), [1,2,3,4] )

		pool = { self.kit23: 4 }
		self.assertEqual( component_availability( pool, self.hdd1, [] ), [1,2,3,4] )
		self.assertEqual( component_availability( pool, self.hdd2, [] ), [1,2,3,4] )

		pool = { self.kit23: 2 }
		self.assertEqual( component_availability( pool, self.hdd1, [ self.hdd1, self.hdd1 ] ), [1,2,3,4] )
	def test_ctrl_with_kit( self ):
		pool = { Feature.objects.get( name = "SATA" ): 2,
			 Feature.objects.get( name = "SAS" ): 4,
			 self.kit2: 2 }
		self.assertEqual( component_availability( pool, self.hdd1, [] ), [1,2] )

		pool[ self.kit2 ] = 4
		self.assertEqual( component_availability( pool, self.hdd1, [] ), [1,2,3,4] )
	def test_lp_and_fp_nics( self ):
		feature_lp = Feature( name = "PCIE_LP" )
		feature_fp = Feature( name = "PCIE_FP" )
		feature_lp.save()
		feature_fp.save()
		subst = Substitution( source = feature_fp, target = feature_lp )
		subst.save()
		component = Component( name = "foobar",
				       component_group = ComponentGroup.objects.get( name = "PLATFORM" ),
				       price = 1.0 )
		component.save()
		requiring = Requiring( component = component, feature = feature_lp, quantity = 1 )
		requiring.save()
		pool = { feature_lp: 1,
			 feature_fp: 2 }
		self.assertEqual( component_availability( pool, component, [] ), [1,2,3] )

class PercentageTest( TestCase ):
	fixtures = [ "test_giver" ]
	def setUp( self ):
		self.computer_model = ComputerModel.objects.get( id = 1 )
		self.platform = Component.objects.get( name = "RSbase" )
		self.warranty = Component( name = "WAR",
					   price = 15.0,
					   component_group = ComponentGroup.objects.get( name = "CTRL" ),
					   is_percentage = True )
		self.warranty.save()
		self.computer_model.components.add( self.warranty )
	def test_percentage( self ):
		self.assertEqual( render( self.computer_model,
					  "%i-%i,%i-%i" % ( self.platform.id, 1,
							    self.warranty.id, 1 ) )["price"], 115.0 )

class DefaultsTest( TestCase ):
	fixtures = [ "test_giver" ]
	def setUp( self ):
		self.computer_model = ComputerModel.objects.get( id = 1 )
		Component.objects.get( id = 3 ).delete() # As we want to test parity too
	def test_default_configuration( self ):
		configuration = self.computer_model.get_default_configuration().split(",")
		correct_one = [ "2-1", "11-1", "4-2" ]
		self.assertEqual( len( configuration ), 3 )
		for ent in correct_one:
			self.assertTrue( ent in configuration )
	def test_default_price( self ):
		self.assertEqual( self.computer_model.get_default_price(), 165.0 )
	def test_default_price_signaling( self ):
		c = Component.objects.get( id = 11 )
		c.price = 200.0
		c.save()
		self.assertEqual( ComputerModel.objects.get( id = 1 ).default_price, 265.0 )

class RequiringsRenderTest( TestCase ):
	fixtures = [ "example" ]
	def setUp( self ):
		self.computer_model1 = ComputerModel.objects.get( alias = "rs120g2" )
		self.computer_model2 = ComputerModel.objects.get( alias = "es330g2" )
	def test_double_requiring( self ):
		self.assertEqual( render( self.computer_model1, self.computer_model1.get_default_configuration() )["groups"][6]["components"][0]["selections"], [ 0 ] )
	def test_multiple_substituted_requiring( self ):
		groups = render( self.computer_model2, "119-1,139-1" )["groups"]
		self.assertEqual( groups[11]["components"][0]["selections"], [ 1, 2 ] )
		self.assertEqual( groups[12]["components"][0]["selections"], [ 1, 2, 3 ] )

class ExpandingTest( TestCase ):
	fixtures = [ "test_giver" ]
	def setUp( self ):
		self.computer_model = ComputerModel.objects.get( id = 1 )
		self.hdd = Component.objects.get( name = "GB250B" )
		self.platform = Component.objects.get( name = "RSbase" )
		self.enclosure = Feature.objects.get( name = "Enclosure35" )
		self.sata = Feature.objects.get( name = "SATA" )

		sata_requiring = Requiring( component = self.hdd,
					    feature = self.sata,
					    quantity = 1,
					    parity = 1 )
		sata_requiring.save()
	def test_initial_availability( self ):
		self.assertEqual( render( self.computer_model, genids({ self.platform: 1, self.hdd: 4 }) )["groups"][3]["components"][0]["quantity"], 2 )
	def test_enclosure_more( self ):
		p = Providing.objects.get( feature = self.enclosure )
		p.quantity = 4
		p.save()
		self.assertEqual( render( self.computer_model, genids({ self.platform: 1, self.hdd: 5 }) )["groups"][3]["components"][0]["quantity"], 4 )
	def test_enclosure_too_many( self ):
		p = Providing.objects.get( feature = self.enclosure )
		p.quantity = 10
		p.save()
		self.assertEqual( render( self.computer_model, genids({ self.platform: 1, self.hdd: 12 }) )["groups"][3]["components"][0]["quantity"], 8 )
	def test_sata_expanding( self ):
		e = Expanding( component = self.platform,
			       feature = self.sata,
			       needed = 2,
			       quantity = 20 )
		e.save()
		p = Providing.objects.get( feature = self.enclosure )
		p.quantity = 10
		p.save()
		self.assertEqual( render( self.computer_model, genids({ self.platform: 1, self.hdd: 12 }) )["groups"][3]["components"][0]["quantity"], 10 )
	def test_sata_expanding2( self ):
		e = Expanding( component = self.platform,
			       feature = self.sata,
			       needed = 2,
			       quantity = 22 )
		e.save()
		p = Providing.objects.get( feature = self.enclosure )
		p.quantity = 20
		p.save()
		self.assertEqual( render( self.computer_model, genids({ self.platform: 1, self.hdd: 22 }) )["groups"][3]["components"][0]["quantity"], 20 )
	def test_unsatisfacted_expanding( self ):
		e = Expanding( component = self.platform,
			       feature = self.sata,
			       needed = 10, # not enough
			       quantity = 20 )
		e.save()
		self.assertEqual( render( self.computer_model, genids({ self.platform: 1, self.hdd: 10 }) )["groups"][3]["components"][0]["quantity"], 2 )

class BigParityTest( TestCase ):
	fixtures = [ "example" ]
	def setUp( self ):
		self.computer_model = ComputerModel.objects.get( alias = "es320g3" )
		self.components_ids = "8-1,140-1,75-1,48-1,117-1,47-4"
	def test_big_parity( self ):
		# Just render it. It should not fail
		render( self.computer_model, self.components_ids )
