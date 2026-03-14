"""functions to manipulate and read from blender meshes/objects

Exceptions

Classes

Functions
    - 'add_spline2data()' -- adds a spline to some existing curve
    - 'apply_rotation()' -- applies the objects rotation (similar to ctrl + A > apply rotation)
    - 'get_bbox()' -- returns bounding box of some object

Other Objects
"""

#%%imports
import bpy

import logging
import numpy as np
from typing import List, Tuple, Union

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

#%%definitions
def add_spline2data(
    data:bpy.types.Curve,
    coords:List[List[float]],
    scale:Union[List[float],float]=1.0,
    handle_type:Union[List[str],str]='AUTO',
    ) -> bpy.types.Spline:
    """adds a new (bezier) spline with vertices at `coords` to `data`

    Parameters
        - `data`
            - `bpy.types.Curve`
            - curve object to add a spline to
        - `coords`
            - `List[List[float]]`
            - coordinates of the vertices defining the new spline
        - `scale`
            - `List[float]`, `float`, optional
            - scale to apply to the vertices' handles
            - if `float`
                - applied to all handles
            - the default is `1.0`
        - `handle_type`
            - `List[str]`, `str`, optional
            - handle type to use for each of the generated vertices
            - if `str`
                - applied to all handles
            - the default is `'AUTO'`

    Raises

    Returns
        - `spline`
            - `bpy.types.Spline`
            - generated spline

    Dependencies
        - `bpy`
        - `logging`
        - `numpy`
        - `typing`
    """
    scale = [scale]*len(coords) if not isinstance(scale, list) else scale
    handle_type = [handle_type]*len(coords) if not isinstance(handle_type, list) else handle_type

    #init spline
    spline = data.splines.new(type='BEZIER')
    
    #deal with first point (splines are initilized with a single vertex)
    spline.bezier_points[0].co = coords[0]
    
    #deal with remaining coords
    for cidx in range(1, len(coords)):

        spline.bezier_points.add(1)                     #append a point
        bp = spline.bezier_points[cidx]                 #reference to new point
        bp.co = coords[cidx]    #set coordinates


    #adjust handle position (needs to be done after creation because context of all coords needed)
    for bp in spline.bezier_points:
        #start with auto to get frame of reference (by default handles are at `bp.co`)
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
        
        #apply handle type (might override handle scaling)
        bp.handle_left_type = handle_type[cidx]
        bp.handle_right_type = handle_type[cidx]
        
        #scale handles
        left_vec = bp.handle_left - bp.co
        right_vec = bp.handle_right - bp.co
        bp.handle_left = bp.co + left_vec * scale[cidx]
        bp.handle_right = bp.co + right_vec * scale[cidx]
        
    return spline

def apply_rotation(
    obj:bpy.types.Object
    ):
    """applies rotation to `obj`

    - equivalent to calling `Ctrl + a > apply rotation` in the UI

    Parameters
        - `obj`
            - `bpy.types.Object`
            - object to apply rotation to

    Raises

    Returns

    Dependencies
        - `bpy`
        - `logging`
        - `numpy`
        - `typing`    
    """
    #get pure rotation
    rot_mat = obj.rotation_euler.to_matrix().to_4x4()

    #bake into vertices
    for v in obj.data.vertices:
        v.co = rot_mat @ v.co

    #reset object rotation
    obj.rotation_euler = (0, 0, 0)
    return {'FINISHED'}

def get_bbox(
    obj:bpy.types.Object
    ) -> Tuple[np.ndarray,np.ndarray]:
    """returns bounding box of `obj`

    Parameters
        - `obj`
            - `bpy.types.Object`
            - object to get bounding box of

    Raises

    Returns
        - `min`
            - `np.ndarray`
            - minimum of the bounding box as `[x,y,z]`
        - `max`
            - `np.ndarray`
            - maximum of the bounding box as `[x,y,z]`

    Dependencies
        - `bpy`
        - `logging`
        - `numpy`
        - `typing`   
    """
    min = np.array([v.co for v in obj.data.vertices]).min(axis=0)
    max = np.array([v.co for v in obj.data.vertices]).max(axis=0)

    return min, max

#%%registration
def register():
    pass
def unregister():
    pass