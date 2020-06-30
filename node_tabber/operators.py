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
    return elem[4]

def write_score(category, enum_items):

    print("Received " + str(enum_items))

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
        print("Content new: ")
        print(content)
        with open(path, "w") as f:
            json.dump(content, f)

        print ("Created :" + path)
    else:
        with open(path, "r") as f:
            content = json.load(f)
        print("Content read: ")
        print(content)
        if enum_items in content:
            print("Match!")
            content[enum_items]['tally'] += 1
        else:
            print("New Node!")
            content[enum_items]={'tally': 1}

        with open(path, "w") as f:
            json.dump(content, f)
        print ("Updated :" + path)

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
        print("Area: " + str(context.space_data.tree_type))

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
                    (str(index),
                     item.label+" ("+short+")",
                     '',
                     index,
                     ))

        #write_score(cat, enum_items)
        #tmp = sorted(enum_items, key=take_fifth, reverse=True)
        return enum_items
        #print(tmp)
        #return tmp

    # Look up the item based on index
    def find_node_item(self, context):
        node_item = int(self.node_item)
        print("Node Item = " + str(node_item))

        for index, item in enumerate(nodeitems_utils.node_items_iter(context)):
            if index == node_item:
                return item
        return None

    node_item: EnumProperty(
        name="Node Type",
        description="Node type",
        items=node_enum_items,
    )
    

    def execute(self, context):
        item = self.find_node_item(context)

        #print(self._enum_item_hack)
        #print(self.node_item)
        #print(self._enum_item_hack[int(self.node_item)][1])
        #print(item.nodetype[0])

        #Add to tally
        write_score(item.nodetype[0], self._enum_item_hack[int(self.node_item)][1])



        # no need to keep
        self._enum_item_hack.clear()

        if item:
            # apply settings from the node item
            for setting in item.settings.items():
                ops = self.settings.add()
                ops.name = setting[0]
                ops.value = setting[1]

            self.create_node(context, item.nodetype)

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



addon_keymaps = []

def register():
    
    bpy.utils.register_class(NodeTabSetting)
    bpy.utils.register_class(NODE_OT_add_tabber_search)

    print("Registered Node Tabber")
    # handle the keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
        kmi = km.keymap_items.new("node.add_tabber_search", type = 'TAB', value= 'PRESS')
        addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(NodeTabSetting)
    bpy.utils.unregister_class(NODE_OT_add_tabber_search)


