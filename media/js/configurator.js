/*
 * ETConf -- web-based user-friendly computer hardware configurator
 * Copyright (C) 2010-2011 ETegro Technologies, PLC <http://etegro.com/>
 *                         Sergey Matveev <sergey.matveev@etegro.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * You can get source code for this engine here: http://sourceforge.net/p/etconf/home/
 */

var FLOWER_PATH = "/img/configurator/flower.gif";

// Dirty hack to force these i18n strings to be parsed
gettext("Updating");
gettext("Ready");
gettext("Shit happens");
gettext("Adding to cart");
gettext("Failed");
gettext("Sending request");

var IDS = {};
var QUANTITY = 1;
var Flower = new Image();

function update_quantity() {
	QUANTITY = $("overall_quantity").value;
};

function parse_get_request() {
	var get = {};
	var get_part = ("" + window.location).split("?")[1];
	if( ! get_part ){ return {} };
	get_part.split("&").each( function( part ) {
		var part_key = part.split("=")[0];
		var part_value = part.split("=")[1];
		get[ part_key ] = part_value;
	} );
	return get;
};

function parse_ids( ids ){
	ids.split(",").each( function( pair ){
		// [ id, quantity ] = pair.split("-"); -- This is not working in lame browsers
		var id = pair.split("-")[0];
		var quantity = pair.split("-")[1];
		IDS[ id ] = quantity;
	} );
};

document.observe("dom:loaded", function(){
	Flower.src = FLOWER_PATH;

	if( typeof parse_get_request()["previous_order"] != "undefined" ){
		parse_ids( parse_get_request()["configuration"] );
		QUANTITY = parse_get_request()["quantity"];
		configurate_perform();
		return;
	};

	new Ajax.Request( $("url").value, {
		method: "get",
		onLoading: function(){
			$("loader").innerHTML = gettext("Retrieving initial configuration");
		},
		onSuccess: function( transport ){
			var response = transport.responseText;
			$("configurator").innerHTML = response;
			$("loader").innerHTML = gettext("Ready");
			parse_ids( $("ids").value );
			update_quantity();
			add_event_handlers();
			remove_alone_selects();
		},
		on404: function() {
			$("configurator").innerHTML = "<p>" + gettext("No such model") + "</p>";
		},
		onFailure: function(){
			$("configurator").innerHTML = "<p>" + gettext("Unable to retrieve initial configuration") + "</p>";
		}
	} );
});

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

function configurate_select() {
};

function configurate_input() {
};

function add_event_handlers() {
	$$("#configurator select").each(
		function(select){ Event.observe(select, 'change', handle_select.bindAsEventListener(select)); }
	);
	$$("#configurator input").each(
		function(input){ Event.observe(input, 'click', handle_input.bindAsEventListener(input)); }
	);
};

function handle_select() {
	var select = this;
	var id = select.name.split("-")[1];
	var input = $("input-" + id);
	var quantity = select.value;

	if (input.type == "radio") { clear_radio(input.name); }
	IDS[ id ] = quantity;
	configurate_perform();
};

function handle_input() {
	var input = this;
	var id = this.value;
	var select = $("select-" + id);
	var quantity = select.value;

	if ( input.type == "radio" ){
		//update only if the current radio button switched on
		if (IDS[ id ] == undefined) {
			clear_radio(input.name);
			IDS[ id ] = quantity;
			configurate_perform();
		};
	} else {
		input.checked ? (IDS[ id ] = quantity) : (delete IDS[ id ]);
		configurate_perform();
	};
};

function clear_radio(name) {
	$$("#configurator input[name=" + name +"]" ).each(
		function(input) { delete IDS[ input.value ]; }
	);
}

function flowerize_inputs() {
	$$("#configurator .input-section").each( function(i){ i.innerHTML = "<img alt='flower' src='" + Flower.src + "' />" } );
	$$("#configurator select").each( function(s){ s.disabled = true } );
};

function configurate_perform() {
	new Ajax.Request( $("url").value, {
		method: "get",
		parameters: { components: serialize_ids(),
			      quantity: QUANTITY },
		onLoading: function(){
			flowerize_inputs();
			$("loader").innerHTML = gettext("Updating");
		},
		onSuccess: function( transport ){
			var response = transport.responseText;
			$("configurator").innerHTML = response;
			$("loader").innerHTML = gettext("Ready");
			add_event_handlers();
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
		parameters: {
			components: serialize_ids(),
			quantity: QUANTITY,
			previous_order: parse_get_request()["previous_order"]
		},
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
