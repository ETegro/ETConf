// ETConf -- web-based user-friendly computer hardware configurator
// Copyright (C) 2010 ETegro Technologies, PLC <http://www.etegro.com/>
//                    Sergey Matveev <sergey.matveev@etegro.com>
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
// 
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

var FLOWER_PATH = "/img/configurator/flower.gif";

var IDS = {};
var Flower = new Image();

window.onload = function(){
	Flower.src = FLOWER_PATH;
	new Ajax.Request( $("url").value, {
		method: "get",
		onLoading: function(){
			$("loader").innerHTML = gettext("Retrieving initial configuration");
		},
		onSuccess: function( transport ){
			var response = transport.responseText;
			$("configurator").innerHTML = response;
			$("loader").innerHTML = gettext("Ready");
			$("ids").value.split(",").each( function( pair ){
				// [ id, quantity ] = pair.split("-"); -- This is not working in lame browsers
				id = pair.split("-")[0];
				quantity = pair.split("-")[1];
				IDS[ id ] = quantity;
			} );
			remove_alone_selects();
		},
		on404: function() {
			$("configurator").innerHTML = "<p>" + gettext("No such model") + "</p>";
		},
		onFailure: function(){
			$("configurator").innerHTML = "<p>" + gettext("Unable to retrieve initial configuration") + "</p>";
		}
	} );
};

function remove_alone_selects() {
	$$("#configurator select").findAll(
		function(s){ return 1 == s.options.length }
	).findAll(
		function(s){ return s.options[0].value == 1 }
	).each(
		function(s){ s.hide() }
	);
};

function serialize_ids() {
	var ids = [];
	for( var id in IDS ){ ids.push( id + "-" + IDS[ id ] ) };
	return ids.join(",");
};

function configurate_select( id, quantity ) {
	IDS[ id ] = quantity;
	configurate_perform();
};

function configurate_input( id ) {
        var input_id = $("input-" + id);
	if( input_id.type == "radio" ){
		$$("#configurator input[name=" + input_id.name +"]" ).each( function( e ){ delete IDS[ e.value ] } );
		IDS[ id ] = $("select-" + id).value;
	} else {
		input_id.checked ? IDS[ id ] = $("select-" + id).value : delete IDS[ id ];
	};
	configurate_perform();
};

function flowerize_inputs() {
	$$("#configurator .input-section").each( function(i){ i.innerHTML = "<img alt='flower' src='" + Flower.src + "' />" } );
	$$("#configurator select").each( function(s){ s.disabled = true } );
};

function configurate_perform() {
	new Ajax.Request( $("url").value, {
		method: "get",
		parameters: { components: serialize_ids() },
		onLoading: function(){
			flowerize_inputs();
			$("loader").innerHTML = gettext("Updating");
		},
		onSuccess: function( transport ){
			var response = transport.responseText;
			$("configurator").innerHTML = response;
			$("loader").innerHTML = gettext("Ready");
			remove_alone_selects();
		},
		onFailure: function(){
			$("loader").innerHTML = gettext("Shit happens");
		}
	} );
};

function cart_add( url ) {
	new Ajax.Request( url, {
		method: "get",
		parameters: { components: serialize_ids() },
		onLoading: function(){
			$("add_to_cart_button").value = gettext("Adding to cart");
		},
		onSuccess: function( transport ){
			var response = transport.responseText;
			window.location = response;
		},
		onFailure: function(){
			$("add_to_cart_button").value = gettext("Failed");
		}
	} );
};

function computermodel_request_send( url ) {
	new Ajax.Request( url, {
		method: "post",
		parameters: { company: $( "id_company" ).value,
			      name: $( "id_name" ).value,
			      address: $( "id_address" ).value,
			      email: $( "id_email" ).value,
			      telephone: $( "id_telephone" ).value,
			      request: $( "id_request" ).value },
		onLoading: function(){
			$("computermodel_request_button").value = gettext("Sending request");
		},
		onSuccess: function( transport ){
			var response = transport.responseText;
			$("computermodel_request_form").innerHTML = response;
		},
		onFailure: function(){
			$("computermodel_request_form").value = gettext("Shit happens");
		}
	} );
};
