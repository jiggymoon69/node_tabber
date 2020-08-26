# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "Node Tabber",
    "author": "Richard Lyons <info@rixiefx.com>",
    "version": (0, 1, 3),
    "blender": (2, 83, 0),
    "description": "Allows quick smart searching of node types.",
    "category": "Node",
}

import bpy
from bpy.types import (
    AddonPreferences,
)
from bpy.props import (
    BoolProperty,
    IntProperty,
)
from . import operators




class node_tabberPreferences(AddonPreferences):
    # This must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.

    bl_idname = __name__

    tally: BoolProperty(
        name="Enable tally count",
        default=True,
        description="Enables Node Tabber to keep a tally of most used nodes, and populate popup accordingly.",
    )
    tally_weight: IntProperty(
        name="Tally Weight",
        default = 12,
        description="Maximum number of tallies for each node selected. Affects the \"weighting\" of the order of tallied results in the node list."
    )
    quick_place: BoolProperty(
        name="Enable \"Quick Place\"",
        default=False,
        description="Allows immediate placement of selected node.",
    )
    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row1 = box.row()
        row2 = box.row()
        row3 = box.row()
        row1.prop(self, "tally")
        row1.operator('node.reset_tally',
                    text = 'Reset Tally')
        row1.prop(self, "tally_weight")
        row2.prop(self, "quick_place")
        row3.label(text="NOTE: CTRL + TAB : Performs \"Edit Group\" functionality.")



def register():
    operators.register()
    bpy.utils.register_class(node_tabberPreferences)

def unregister():
    operators.unregister()
    bpy.utils.unregister_class(node_tabberPreferences)

