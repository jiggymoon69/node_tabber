import bpy
import json
import os
import nodeitems_utils
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




# Base class for node 'Add' operators
class NodeAddTabOperator:

    type: StringProperty(
        name="Node Type",
        description="Node type",
    )
    use_transform: BoolProperty(
        name="Use Transform",
        description="Start transform operator after inserting the node",
        default=True,
    )
    settings: CollectionProperty(
        name="Settings",
        description="Settings to be applied on the newly created node",
        type=NodeTabSetting,
        options={'SKIP_SAVE'},
    )

    @staticmethod
    def store_mouse_cursor(context, event):
        space = context.space_data
        tree = space.edit_tree

        # convert mouse position to the View2D for later node placement
        if context.region.type == 'WINDOW':
            # convert mouse position to the View2D for later node placement
            space.cursor_location_from_region(
                event.mouse_region_x, event.mouse_region_y)
        else:
            space.cursor_location = tree.view_center

    # XXX explicit node_type argument is usually not necessary,
    # but required to make search operator work:
    # add_search has to override the 'type' property
    # since it's hardcoded in bpy_operator_wrap.c ...
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

        for setting in self.settings:
            # XXX catch exceptions here?
            value = eval(setting.value)

            try:
                setattr(node, setting.name, value)
            except AttributeError as e:
                self.report(
                    {'ERROR_INVALID_INPUT'},
                    "Node has no attribute " + setting.name)
                print(str(e))
                # Continue despite invalid attribute

        node.select = True
        tree.nodes.active = node
        node.location = space.cursor_location
        return node

    @classmethod
    def poll(cls, context):
        space = context.space_data
        # needs active node editor and a tree to add nodes to
        return ((space.type == 'NODE_EDITOR') and
                space.edit_tree and not space.edit_tree.library)

    # Default execute simply adds a node
    def execute(self, context):
        if self.properties.is_property_set("type"):
            self.create_node(context)
            print("Added node in default execute")
            return {'FINISHED'}
        else:
            return {'CANCELLED'}

    # Default invoke stores the mouse position to place the node correctly
    # and optionally invokes the transform operator
    def invoke(self, context, event):
        self.store_mouse_cursor(context, event)
        result = self.execute(context)

        if self.use_transform and ('FINISHED' in result):
            # removes the node again if transform is canceled
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        return result



class NODE_OT_add_tabber_search(NodeAddTabOperator, bpy.types.Operator):
    '''Add a node to the active tree using node tabber'''
    bl_idname = "node.add_tabber_search"
    bl_label = "Search and Add Node"
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "node_item"

    _enum_item_hack = []

    # Create an enum list from node items
    def node_enum_items(self, context):
        enum_items = NODE_OT_add_tabber_search._enum_item_hack

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
                potato = [str(index), tally]

                enum_items.append(
                    (str(index) + " 0 0",
                     item.label+" ("+short+")",
                     str(tally),
                     index,
                     ))

                #temp test 
                if item.label == "Math":
                    #print("Found math node at index " + str(index))
                    enum_items.append(
                    (str(index) + " M SUBTRACT",
                     "Subtract (S)",
                     str(tally),
                     index+1,
                     ))

        #print (enum_items[0])
        addon = bpy.context.preferences.addons['node_tabber']
        prefs = addon.preferences

        if prefs.tally:
            tmp = enum_items
            #tmp.sort(key = lambda tmp: int(tmp[2]), reverse = True)
            tmp = sorted(enum_items, key=take_fifth, reverse=True)
            print("\n\n" + str(tmp) + "\n\n")
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
                print ("Item : " + str(item))
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
            print("extra 0: " + str(extra[0]))
            print("extra 1: " + str(extra[1]))
            # print ("Hack0 : " + str(self._enum_item_hack[int(self.node_item)][0]))
            # print ("Hack1 : " + str(self._enum_item_hack[int(self.node_item)][1]))
            # print ("Hack2 : " + str(self._enum_item_hack[int(self.node_item)][2]))
            # print ("Hack3 : " + str(self._enum_item_hack[int(self.node_item)][3]))
            # print ("Hack4 : " + str(self._enum_item_hack[int(self.node_item)][4]))

            if (extra[0] == "M"):
                print("Math node to subtract")
                space = context.space_data
                node_tree = space.node_tree
                node_active = context.active_node
                node_selected = context.selected_nodes

                node_active.operation = "SUBTRACT"

            if self.use_transform:
                bpy.ops.node.translate_attach_remove_on_cancel(
                    'INVOKE_DEFAULT')

            return {'FINISHED'}
        else:
            return {'CANCELLED'}

    def invoke(self, context, event):
        self.store_mouse_cursor(context, event)
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


