"""
"""

#%%imports
import bpy

import logging

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

#%%registration
def register():
    pass
def unregister():
    pass