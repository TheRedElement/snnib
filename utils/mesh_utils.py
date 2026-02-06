"""
"""

#%%imports
import bpy

import logging
from typing import List

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

#%%definitions
def add_spline2data(
    data:bpy.types.Curve,
    coords:List[List],
    ) -> bpy.types.Spline:
    """adds a new spline with vertices at `coords` to `data`
    """

    #init spline
    spline = data.splines.new(type='BEZIER')
    
    #deal with first point (splines are initilized with a single vertex)
    spline.bezier_points[0].co = coords[0]
    
    #deal with remainig coords
    for cidx in range(1, len(coords)):
        spline.bezier_points.add(1)                    #append a point
        spline.bezier_points[cidx].co = coords[cidx]    #set coordinates

    #automate handle position (needs to be done after creation because context of all coords needed)
    for p in spline.bezier_points:
        p.handle_left_type = 'AUTO'
        p.handle_right_type = 'AUTO'    
        
    return spline

#%%registration
def register():
    pass
def unregister():
    pass