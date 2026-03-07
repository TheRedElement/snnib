"""
"""

#%%imports
import bpy

import logging
import numpy as np
from typing import List, Tuple

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

#%%definitions
def add_spline2data(
    data:bpy.types.Curve,
    coords:List[List],
    scale:List[float]=1.0,
    handle_type:List[str]='AUTO',
    ) -> bpy.types.Spline:
    """adds a new spline with vertices at `coords` to `data`
    """
    scale = [scale]*len(coords) if not isinstance(scale, list) else scale
    handle_type = [handle_type]*len(coords) if not isinstance(handle_type, list) else handle_type

    #init spline
    spline = data.splines.new(type='BEZIER')
    
    #deal with first point (splines are initilized with a single vertex)
    spline.bezier_points[0].co = coords[0]
    
    #deal with remainig coords
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

def apply_rotation(obj:bpy.types.Object):
    """applies rotation to `obj`
    """
    #get pure rotation
    rot_mat = obj.rotation_euler.to_matrix().to_4x4()

    #bake into vertices
    for v in obj.data.vertices:
        v.co = rot_mat @ v.co

    #reset object rotation
    obj.rotation_euler = (0, 0, 0)
    return {'FINISHED'}

def get_bbox(obj:bpy.types.Object) -> Tuple[np.ndarray,np.ndarray]:

    min = np.array([v.co for v in obj.data.vertices]).min(axis=0)
    max = np.array([v.co for v in obj.data.vertices]).max(axis=0)

    return min, max

#%%registration
def register():
    pass
def unregister():
    pass