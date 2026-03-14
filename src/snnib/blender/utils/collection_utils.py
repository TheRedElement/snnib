"""functions to deal with `bpy.types.Collection`

Exceptions

Classes

Functions
    - `ensure_collection()` -- ensures that a collection exists
    - `clear_collection()` -- recursively deletes all object in a collection
    - `obj_unlink_all_collections()` -- unlinks an object from all of it's current collections

Other Objects
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

    Raises

    Returns
        - `current`
            - `bpy.types.Collection`
            - collection of `name`

    Dependencies
        - `bpy`
        - `logging`
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

def clear_collection(
    collection:bpy.types.Collection
    ):
    """recursively deletes all objects in `collection`
    
    - deletes all objects in `collection`
    - also unliks them everywhere else

    Parameters
        - `collection`
            - `bpy.types.Collection`
            - collection to delete all objects contained within
    Raises

    Returns

    Dependencies
        - `bpy`
        - `logging`
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
    """unlinks object from all of its current collections

    Parameters
        - `obj`
            - `bpy.types.Object`
            - object to unlink from all collections

    Raises

    Returns

    Dependencies
        - `bpy`
        - `logging`
    """
            
    for c in obj.users_collection:
        c.objects.unlink(obj)    
    
    return

#%%registration
def register():
    pass
def unregister():
    pass