"""utilities to manipulate blenders geometry nodes

Exceptions

Classes

Functions
    - `add_todo_node()`
    - `copy_geonodes()`
    - `clear_node_group()`
    - `create_node_group()`
    - `delete_geonode_groups()`
    - `exists_node_group()`
    - `get_node_by_label()`
    - `set_node_curve()`

Other Objects
"""

#%%imports
import bpy

import logging
from typing import List, Tuple, Union

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

#%%definitions
def add_todo_node(
    node_group:bpy.types.GeometryNodeTree,
    location:Tuple[float,float]=(0.0,0.0),
    ) -> bpy.types.Node:
    """adds a frame denoting a TODO to the node tree

    Parameters
        - `node_group`
            - `bpy.types.GeometryNodeTree`
            - geo nodes node tree to attach the node to
        - `location`
            - `Tuple[float,float]`, optional
            - location as `(x,y)` of the node
            - the default is `(0.0,0.0)`

    Raises

    Returns
        - `n_todo`
            - `bpy.types.Node`
            - created node

    Dependencies
        - `bpy`
        - `logging`
        - `typing`
    """
    n_todo = node_group.nodes.new(type="NodeFrame")
    n_todo.label = "TODO"
    n_todo.use_custom_color = True
    n_todo.label_size = 45
    n_todo.color = (1.0,0.4,0.0)
    n_todo.location = location

    return n_todo

def copy_geonodes(
    src:bpy.types.Object, targ:bpy.types.Object,
    ) -> bpy.types.NodesModifier:
    """sets the geo nodes modifier of `targ` to the same as `src`

    - only applies to first found geo nodes modifier
    - no action if no geo nodes modifier found

    Parameters
        - `src`
            - `bpy.types.Object`
            - source to copy geo nodes modifier from
        - `targ`
            - `bpy.types.Object`
            - target to copy geo nodes modifier to

    Raises

    Returns
        - `targ_gn_mod`
            - `bpy.types.NodesModifier`
            - created geo nodes modifier

    Dependencies
        - `bpy`
        - `logging`
        - `typing`    
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

def clear_node_group(
    group_name:str
    ):
    """clears the node group of `group_name`

    - used to avoid cluttering in blender file when developing new node group
    - allow to stay in node group and see changes when rerunning scripts

    Parameters
        - `group_name`
            - `str`
            - name of the targeted geo nodes group

    Raises

    Returns

    Dependencies
        - `bpy`
        - `logging`
        - `typing`       
    """
    for ng in bpy.data.node_groups:
        if group_name==ng.name:
            ng.nodes.clear()
            ng.links.clear()
            ng.interface.clear()
    return {'FINISHED'}

def create_node_group(
    group_name:str, dev:bool
    ) -> bpy.types.GeometryNodeTree:
    """returns existing node group if `dev`, otherwise always creates new one
    
    - helper creating node groups based on specifications
    - overrides existing nodes when `dev==True` (creates new group if nonexistent)
    - creates new group without overriding if `dev!=True`

    Parameters
        - `group_name`
            - `str`
            - name of the targeted geo nodes group
        - `dev`
            - `bool`, optional
            - flag denoting if script is ran in development mode

    Raises

    Returns
        - `node_group`
            - `bpy.types.GeometryNodeTree`
            - created geo nodes node group

    Dependencies
        - `bpy`
        - `logging`
        - `typing`      
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

def delete_geonode_groups(
    group_name:str
    ):
    """deletes all geometry node node groups with name `group_name`
    
    - used before generating new groups to avoid cluttering blender

    Parameters
        - `group_name`
            - `str`
            - name of the targeted geo nodes group

    Raises

    Returns

    Dependencies
        - `bpy`
        - `logging`
        - `typing`          
    """
    
    #get all matching goroups
    to_delete = [ng for ng in bpy.data.node_groups if ng.name == group_name and ng.bl_idname == "GeometryNodeTree"]

    #remove found groups
    for ng in to_delete:
        bpy.data.node_groups.remove(ng)

    return {'FINISHED'}

def exists_node_group(
    group_name:str
    ):
    """returns flag whether node group of `group_name` already exists

    - used to avoid cluttering in blender file when developing new node group
        - allows creation of new group only if it is not existing already

    Parameters
        - `group_name`
            - `str`
            - name of the targeted geo nodes group

    Raises

    Returns

    Dependencies
        - `bpy`
        - `logging`
        - `typing`           
    """
    return any([group_name==ng.name for ng in bpy.data.node_groups])

def get_node_by_label(
    node_tree:bpy.types.GeometryNodeTree,
    label:str,
    ) -> bpy.types.Node:
    """returns first node in `node_tree` that matches `label`

    Parameters
        - `node_tree`
            - `bpy.types.GeometryNodeTree`
            - geometry nodes node tree to extract node from
        - `label`
            - `str`
            - label of the node to search for

    Raises

    Returns
        - `node`
            - `bpy.types.Node`
            - extracted node
            - `None` if no matching node was found

    Dependencies
        - `bpy`
        - `logging`
        - `typing`       
    """
    for node in node_tree.nodes:
        if node.label == label:
            return node
    return None

def set_node_curve(
    node:bpy.types.ShaderNodeRGBCurve,
    channel_index:int,
    pts:List[List[float]],
    handle_types:List[str]=None
    ):
    """overrides node curve (i.e. RGB Curves node) with new curve

    Parameters
        - `node`
            - `bpy.types.ShaderNodeRGBCurve`
            - node to update the curve of
        - `channel_index`
            - `int`
            - index of the channel to target
                - 0 > r
                - 1 > g
                - 2 > b
                - 3 > combined
        - `pts`
            - `List[List[float]]`
            - coordinates to place the control points at
        - `handle_types`
            - `List[str]`, optional
            - handle types to use for each point in `pts`
            - the default is `None`
                - uses default settings
            
    Raises

    Returns

    Dependencies
        - `bpy`
        - `logging`
        - `typing`     
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


#%%registration
def register():
    pass
def unregister():
    pass