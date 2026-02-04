"""
"""

#%%imports
import bpy

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

#%%definitions
def ensure_collection(
    path:str,
    parent:bpy.types.Collection=None,
    ) -> bpy.types.Collection:
    """returns collection of `name`

    - returns collection of `name`
    - creates new collection of `name`, if non-existent
    
    Parameters
        - `path`
            - `str`
            - path to the collection relative to `parent`
            - path to the collection as `Parent0/Parent1/.../Child`
        - `parent`
            - `bpy.types.Collection`, optional
            - parent collection
            - the default is `None`
                - uses `bpy.context.scene.collection`
    """

    if parent is None:
        parent = bpy.context.scene.collection

    current = parent
    for name in path.split("/"):
        child = current.children.get(name)
        if child is None:
            child = bpy.data.collections.new(name)
            current.children.link(child)
        current = child

    return current

def clear_collection(collection):
    """deletes all objects in `collection`
    
    - deletes all objects in `collection`
    - also unliks them everywhere else
    """
    #remove objects
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    
    #recursive removal of subcollections
    for child in list(collection.children):
        clear_collection(child)
        bpy.data.collections.remove(child)
        
    return

def obj_unlink_all_collections(
    obj:bpy.types.Object
    ):
    """unlinks object from all of it's current collections
    """
            
    for c in obj.users_collection:
        c.objects.unlink(obj)    
    
    return

#%%registration
def register():
    pass
def unregister():
    pass