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

from django.conf.urls.defaults import *

urlpatterns = patterns( "configurator.creator.views",
	( r"^move/component/up/(?P<component_id>\d+)$", "move_component_up" ),
	( r"^move/component/down/(?P<component_id>\d+)$", "move_component_down" ),
	( r"^move/specification_key/up/(?P<specification_key_id>\d+)$", "move_specification_key_up" ),
	( r"^move/specification_key/down/(?P<specification_key_id>\d+)$", "move_specification_key_down" ),
	( r"^move/component_group/up/(?P<component_group_id>\d+)$", "move_component_group_up" ),
	( r"^move/component_group/down/(?P<component_group_id>\d+)$", "move_component_group_down" ),
	( r"^move/subsystem/up/(?P<subsystem_id>\d+)$", "move_subsystem_up" ),
	( r"^move/subsystem/down/(?P<subsystem_id>\d+)$", "move_subsystem_down" ),

	( r"^clone/component/(?P<component_id>\d+)$", "clone_component" ),
	( r"^clone/computermodel/(?P<computermodel_id>\d+)$", "clone_computermodel" ),
	( r"^render/rst/(?P<computermodel_alias>\w+)$", "render_rst" ),
	( r"^render/pdf/(?P<computermodel_alias>\w+)$", "render_pdf" ),
	( r"^specifications/clone/(?P<computermodel_src_alias>\w+)/(?P<computermodel_dst_alias>\w+)/$", "specifications_clone" ),
	( r"^components/editor/(?P<computermodel_alias>\w+)/$", "components_editor" ),
	( r"^component/edit/$", "component_edit" ),
	( r"^specification/edit/(?P<computermodel_alias>\w+)/$", "specification_edit" ),
	( r"^computermodel/edit/(?P<computermodel_alias>\w+)/$", "computermodel_edit" ),
)
