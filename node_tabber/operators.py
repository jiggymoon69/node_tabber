import bpy
import json
import os
import nodeitems_utils
from . import nt_extras
from bpy.types import (
    Operator,
    PropertyGroup,
)
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    IntProperty,
    StringProperty,
)


def take_fifth(elem):
    return int(elem[2])

def write_score(category, enum_items):

    addon = bpy.context.preferences.addons['node_tabber']
    prefs = addon.preferences

    #print("Received " + str(enum_items))

    if (category == "S"):
        category = "shader.json"
    if (category == "C"):
        category = "compositor.json"
    if (category == "T"):
        category = "texture.json"


    path = os.path.dirname(__file__) + "/" + category
    if not os.path.exists(path):
        content = {}
        content[enum_items]={'tally': 1}
        #print("Content new: ")
        #print(content)
        with open(path, "w") as f:
            json.dump(content, f)

        print ("Nodetabber created :" + path)
    else:
        with open(path, "r") as f:
            content = json.load(f)
        #print("Content read: ")
        #print(content)
        if enum_items in content:
            #print("Match!")
            if (content[enum_items]['tally'] < prefs.tally_weight):
                content[enum_items]['tally'] += 1
        else:
            #print("New Node!")
            content[enum_items]={'tally': 1}

        with open(path, "w") as f:
            json.dump(content, f)
        #print ("Updated :" + path)

    return


class NodeTabSetting(PropertyGroup):
    value: StringProperty(
        name="Value",
        description="Python expression to be evaluated "
        "as the initial node setting",
        default="",
    )




class NODE_OT_add_tabber_search(bpy.types.Operator):
    '''Add a node to the active tree using node tabber'''
    bl_idname = "node.add_tabber_search"
    bl_label = "Search and Add Node"
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "node_item"

    _enum_item_hack = []

    # Create an enum list from node items
    def node_enum_items(self, context):
        enum_items = NODE_OT_add_tabber_search._enum_item_hack

        #extra_math = [[" M ADD", "Add (A) MATH"], [" M SUBTRACT", "Subtract (S) MATH"], [" M MULTIPLY", "Multiply (M) MATH"], [" M DIVIDE", "Divide (D) MATH"], [" M ABSOLUTE", "Absolute (A) MATH"],  [" M PINGPONG", "Ping-Pong (PP) MATH"]]

        enum_items.clear()
        category = context.space_data.tree_type[0]

        if (category == "S"):
            category = "shader.json"
        if (category == "C"):
            category = "compositor.json"
        if (category == "T"):
            category = "texture.json"

        path = os.path.dirname(__file__) + "/" + category
        if not os.path.exists(path):
            content = {}
        else:
            with open(path, "r") as f:
                content = json.load(f)


        for index, item in enumerate(nodeitems_utils.node_items_iter(context)):
            if isinstance(item, nodeitems_utils.NodeItem):

                short = ''
                tally = 0
                words = item.label.split()
                for word in words:
                    short += word[0]
                match = item.label+" ("+short+")"
                if match in content:
                    tally = content[match]['tally']

                enum_items.append(
                    (str(index) + " 0 0",
                     item.label+" ("+short+")",
                     str(tally),
                     index,
                     ))

                #temp test 
                if item.label == "Math":
                    for index2, subname in enumerate(nt_extras.extra_math):
                        enum_items.append(
                            (str(index) + subname[0],
                            subname[1],
                            str(0),
                            index+1+index2,
                        ))


                # if item.label == "Vector Math":
                #     #print("Found math node at index " + str(index))
                #     enum_items.append(
                #     (str(index) + " VM SUBTRACT",
                #     "Subtract (S) VECTOR MATH",
                #     str(0),
                #     index+3,
                #     ))

        #print (enum_items[0])
        addon = bpy.context.preferences.addons['node_tabber']
        prefs = addon.preferences

        if prefs.tally:
            tmp = enum_items
            #tmp.sort(key = lambda tmp: int(tmp[2]), reverse = True)
            tmp = sorted(enum_items, key=take_fifth, reverse=True)
           # print("\n\n" + str(tmp) + "\n\n")
        else:
            tmp = enum_items
        return tmp
        #return enum_items


    # Look up the item based on index
    def find_node_item(self, context):
        tmp = int(self.node_item.split()[0])
        print("tmp : " + str(self.node_item.split()))
        #node_item = int(self.node_item)
        node_item = tmp
        extra = [self.node_item.split()[1], self.node_item.split()[2]]
        print ("First extra :" + str(extra))
        

        for index, item in enumerate(nodeitems_utils.node_items_iter(context)):
            if index == node_item:
                return [item, extra]
        return None

    node_item: EnumProperty(
        name="Node Type",
        description="Node type",
        items=node_enum_items,
    )
    

    def execute(self, context):
        item = self.find_node_item(context)[0]
        extra = self.find_node_item(context)[1]
        #Add to tally
        #write_score(item.nodetype[0], self._enum_item_hack[int(self.node_item)][1])
        short = ''
        words = item.label.split()
        for word in words:
            short += word[0]
        match = item.label+" ("+short+")"

        write_score(item.nodetype[0], match)

        print ("Writing : ")
       # print ("Hack0 : " + str(self._enum_item_hack)[])
        print ("Hack")
        print (self.node_item)
        print (self._enum_item_hack[int(self.node_item[0]) -0][1])
        print (item.label)

        # no need to keep
        self._enum_item_hack.clear()

        if item:
            # apply settings from the node item
            for setting in item.settings.items():
                ops = self.settings.add()
                ops.name = setting[0]
                ops.value = setting[1]

            self.create_node(context, item.nodetype)
            #print("Added node in node tabber")
            
            print(str(item.nodetype))
            #print(str(item.nodename))
            print("extra 0: " + str(extra[0]))
            print("extra 1: " + str(extra[1]))

            
            space = context.space_data
            node_tree = space.node_tree
            node_active = context.active_node
            node_selected = context.selected_nodes

            if (extra[0] == "M"):
                node_active.operation = extra[1]

            if (extra[0] == "VM"):
                node_active.operation = extra[1]

            #if self.use_transform:
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

            return {'FINISHED'}
        else:
            return {'CANCELLED'}

    def create_node(self, context, node_type=None):
        space = context.space_data
        tree = space.edit_tree

        if node_type is None:
            node_type = self.type

        #print("Node Type: " + str(node_type))
        # select only the new node
        for n in tree.nodes:
            n.select = False

        node = tree.nodes.new(type=node_type)

        node.select = True
        tree.nodes.active = node
        node.location = space.cursor_location
        return node

    def invoke(self, context, event):
        #self.store_mouse_cursor(context, event)
        # Delayed execution in the search popup
        context.window_manager.invoke_search_popup(self)
        return {'CANCELLED'}

class NODE_OT_reset_tally(bpy.types.Operator):
    '''Reset the tally count'''
    bl_idname = "node.reset_tally"
    bl_label = "Reset node tally count"

    def execute(self, context):
        categories = ["shader.json", "compositor.json", "texture.json"]
        reset = False
        for cat in categories:
            path = os.path.dirname(__file__) + "/" + cat
            if os.path.exists(path):
                reset = True
                # delete file
                os.remove(path)
                            
            if reset:
                info = ("Reset Tallies")
                self.report({'INFO'}, info)
            else:
                info = ("No tallies to reset.")
                self.report({'INFO'}, info)


        return {'FINISHED'}


addon_keymaps = []

def register():
    
    bpy.utils.register_class(NodeTabSetting)
    bpy.utils.register_class(NODE_OT_add_tabber_search)
    bpy.utils.register_class(NODE_OT_reset_tally)

    #print("Registered Node Tabber")
    # handle the keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
        kmi = km.keymap_items.new("node.add_tabber_search", type = 'TAB', value= 'PRESS')
        kmj = km.keymap_items.new("node.group_edit", type = 'TAB', value= 'PRESS', ctrl= True)
        addon_keymaps.append((km, kmi, kmj))

def unregister():
    for km, kmi, kmj in addon_keymaps:
        km.keymap_items.remove(kmi)
        km.keymap_items.remove(kmj)
    addon_keymaps.clear()

    bpy.utils.unregister_class(NodeTabSetting)
    bpy.utils.unregister_class(NODE_OT_add_tabber_search)
    bpy.utils.unregister_class(NODE_OT_reset_tally)


