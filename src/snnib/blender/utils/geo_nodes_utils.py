"""
"""

#%%imports
import bpy

import logging
from typing import List, Union

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

#%%definitions
def copy_geonodes(
    src:bpy.types.Object, targ:bpy.types.Object,
    ) -> bpy.types.NodesModifier:
    """sets the geonodes modifier of `targ` to the same as `src`
    """
    
    #get source modifier
    src_gn_mod = None
    for mod in src.modifiers:
        if mod.type == "NODES":
            src_gn_mod = mod
            break

    if src_gn_mod is None:
        logger.warning("no geonodes found... ignoring...")
        return {'FINISHED'}

    # Add a new Geometry Nodes modifier to the target
    targ_gn_mod = targ.modifiers.new(name=src_gn_mod.name, type='NODES')

    # Copy the node group from the source modifier
    targ_gn_mod.node_group = src_gn_mod.node_group
    
    return targ_gn_mod

def delete_geonode_groups(group_name:str):
    """deletes all geometry node node groups with name `group_name`
    
    - used before generating new groups to avoid cluttering blender
    """
    
    #get all matching goroups
    to_delete = [ng for ng in bpy.data.node_groups if ng.name == group_name and ng.bl_idname == "GeometryNodeTree"]

    #remove found groups
    for ng in to_delete:
        bpy.data.node_groups.remove(ng)

    return {'FINISHED'}

def exists_node_group(group_name:str):
    """returns flag whether node group of `group_name` already exists

    - used to avoid cluttering in blender file when developing new node group
        - allows creation of new group only if it is not existing already
    """
    return any([group_name==ng.name for ng in bpy.data.node_groups])

def clear_node_group(group_name:str):
    """clears the node group of `group_name`

    - used to avoid cluttering in blender file when developing new node group
    - allow to stay in node group and see changes when rerunning scripts
    """
    for ng in bpy.data.node_groups:
        if group_name==ng.name:
            ng.nodes.clear()
            ng.links.clear()
            ng.interface.clear()
    return {'FINISHED'}

def create_node_group(group_name:str, dev:bool) -> Union[bpy.types.GeometryNodeTree,bpy.types.ShaderNodeTree]:
    """returns existing node group if `dev`, otherwise always creates new one
    
    - helper creating node groups based on specifications
    - overrides existing nodes when `dev==True` (creates new group if nonexistent)
    - creates new group without overriding if `dev!=True`
    """
    #node creation
    if dev:
        clear_node_group(group_name)
        if not exists_node_group(group_name):
            #new node group if it does not exist yet
            node_group = bpy.data.node_groups.new(name=group_name, type='GeometryNodeTree')    
        else:
            node_group = bpy.data.node_groups[group_name]
    else:
        #new node group regardless (will enumerate if existent)
        node_group = bpy.data.node_groups.new(name=group_name, type='GeometryNodeTree')    

    return node_group

def set_node_curve(node:bpy.types.ShaderNodeRGBCurve, channel_index:int, pts:List[List[float]], handle_types:List[str]=None):
    """overrides node curve (i.e. RGB Curves node) with new curve
    """
    curve = node.mapping.curves[channel_index]
    
    #keep endpoints only
    while len(curve.points) > 2:
        curve.points.remove(curve.points[1])
    
    for (x, y) in pts:
        curve.points.new(x, y)

    #remove old first points
    curve.points.remove(curve.points[0])
    #remove old last points
    # for p in curve.points: print(p.location)
    curve.points.remove(curve.points[-2])
    
    #set handle types
    if handle_types is not None:
        for idx, ht in enumerate(handle_types):
            curve.points[idx].handle_type = ht

    #apply changes
    node.mapping.update()
    return  {'FINISHED'}

def add_todo_node(node_group, location=(0,0)):
    """adds a frame denoting a TODO to the node tree
    """
    n_todo = node_group.nodes.new(type="NodeFrame")
    n_todo.label = "TODO"
    n_todo.use_custom_color = True
    n_todo.label_size = 45
    n_todo.color = (1.0,0.4,0.0)
    n_todo.location = location

    return n_todo

#%%registration
def register():
    pass
def unregister():
    pass