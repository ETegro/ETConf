{% comment %}
ETConf -- web-based user-friendly computer hardware configurator
Copyright (C) 2010-2011 ETegro Technologies, PLC <http://etegro.com/>
                        Sergey Matveev <sergey.matveev@etegro.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
{% endcomment %}

{% load i18n %}

var ACTIVE_PAGE="";

window.onload = function() {
	{% for group in groups %}
	Sortable.create( "{{ group.group.name }}_included",
			 { containment: [ "{{ group.group.name }}_included",
			 		  "{{ group.group.name }}_available" ],
			   dropOnEmpty: true } );
	Sortable.create( "{{ group.group.name }}_available",
			 { containment: [ "{{ group.group.name }}_included",
			 		  "{{ group.group.name }}_available" ],
			   dropOnEmpty: true } );
	stretch_list( "{{ group.group.name }}" );
	{% endfor %}

	// Hide all pages except component's editor
	$("components-editor-page").show();
	$("specification-editor-page").hide();
	$("computermodel-editor-page").hide();
	ACTIVE_PAGE = "components-editor-page";
};

function submit_components() {
	ids = [];
	{% for group in groups %}
	ids = ids.concat( Sortable.serialize( "{{ group.group.name }}_included" ).split("&").collect( function(s){ return s.split("=")[1] } ) );
	{% endfor %}
	new Ajax.Request( "{% url configurator.creator.views.components_editor computermodel.alias %}", {
		method: "post",
		parameters: { "ids": ids.join(",") },
		onSuccess: function( transport ){
			var response = transport.responseText;
			window.location = response;
		},
		onFailure: function(){
			alert("{% trans "Shit happens" %}");
		}
	} );
};

function switch_model( alias ){
	window.location = "{% url configurator.creator.views.components_editor "foo" %}".replace("foo", alias );
};

function component_edit( group_name, component_id ){
	new Ajax.Request( "{% url configurator.creator.views.component_edit %}", {
		method: "post",
		parameters: { "component_id": component_id },
		onSuccess: function( transport ){
			var response = transport.responseText;
			var div_id = group_name + "_component_editor";
			$(div_id).hide();
			$(div_id).innerHTML = response;
			Effect.toggle( div_id, "slide" );
		},
		onFailure: function(){
			alert("{% trans "Shit happens" %})");
		}
	} );
};

function component_edit_submit( group_name, component_id ){
	new Ajax.Request( "{% url configurator.creator.views.component_edit %}", {
		method: "post",
		parameters: { "component_id": component_id,
			      "name": $( component_id + "_name" ).value,
			      "description": $( component_id + "_description" ).value,
			      "price": $( component_id + "_price" ).value,
			      "is_percentage": $( component_id + "_is_percentage" ).checked },
		onSuccess: function( transport ){
			var response = transport.responseText;
			var div_id = group_name + "_component_editor";
			if( response == "saved" ){
				Effect.toggle( div_id, "slide" );
			} else {
				$(div_id).innerHTML = response;
			};
		},
		onFailure: function(){
			alert("{% trans "Shit happens" %}");
		}
	} );
};

function component_edit_cancel( group_name ){
	var div_id = group_name + "_component_editor";
	Effect.toggle( div_id, "slide" );
};

function stretch_list( group_name ){
	MAX_ELEMENTS = 6;
	available = $( group_name + "_available" );
	included = $( group_name + "_included" );
	max = Math.max( available.childElements().length,
			included.childElements().length );
	if( max >= MAX_ELEMENTS ) return;
	available.setStyle({ "height": (2 + max) + "em" });
	included.setStyle({ "height": (2 + max) + "em" });
};

function show_page( page_name ){
	if( page_name == ACTIVE_PAGE ) return;
	$(page_name).show();
	$(ACTIVE_PAGE).hide();
	ACTIVE_PAGE = page_name;
};

function specifications_submit(){
	parameters = {
	{% for specification_key in specification_keys %}
		"{{ specification_key.id }}": $("{{ specification_key.id }}_svalue").value,
	{% endfor %}
	};
	new Ajax.Request( "{% url configurator.creator.views.specification_edit computermodel.alias %}", {
		method: "post",
		"parameters": parameters,
		onSuccess: function( transport ){
			var response = transport.responseText;
			$("specification-editor-page").innerHTML = response;
			show_page( "components-editor-page" );
		},
		onFailure: function(){
			alert("{% trans "Shit happens" %}");
		}
	} );
};

function computermodel_submit(){
	new Ajax.Request( "{% url configurator.creator.views.computermodel_edit computermodel.alias %}", {
		method: "post",
		parameters: { "description": $("id_description").value,
			      "slogan": $("id_slogan").value },
		onSuccess: function( transport ){
			var response = transport.responseText;
			$("computermodel-editor-page").innerHTML = response;
		},
		onFailure: function(){
			alert("{% trans "Shit happens" %}");
		}
	} );
};
