"""
"""

#%%imports
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

import numpy as np

import logging
from typing import List

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

#%%definitions
def random_points_bbox(
    obj:bpy.types.Object,
    Rng:np.random.Generator,
    n:int=1,
    ) -> np.ndarray:
    """generates `n` random points inside the bounding box of `object`
    """

    #generate neurons at random locations
    min = np.array([v.co for v in obj.data.vertices]).min(axis=0)
    max = np.array([v.co for v in obj.data.vertices]).max(axis=0)

    coords = Rng.random((n,3)) * (max - min) + min

    return coords

def random_points_raycast(
    obj:bpy.types.Object,
    Rng:np.random.Generator,
    n:int=1,
    ) -> np.ndarray:
    """generates a single random point inside `obj`
    """

    def is_point_inside(
        point:Vector,
        bvh:BVHTree,
        ) -> bool:
        """determine if a point is inside some geometry

        - cast a ray in +X direction.
            - if surface hit an odd number of times => point is inside.
        """
        direction = Vector([1, 0, 0])   #raycast direction
        hit_count = 0                   #init hit-count
        origin = point                  #ray-origin

        while True:
            hit = bvh.ray_cast(origin, direction)   #cast a ray
            if not hit[0]:  #case: no intersection at all
                break
            
            #increase hit-count
            hit_count += 1
            
            #move origin slightly forward => avoids hitting same face again
            origin = hit[0] + direction * 1e-6
            print(origin)

        return (hit_count % 2) == 1


    #get evaluated mesh (modifiers applied)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)

    #build BVH for fast ray tests
    bvh = BVHTree.FromObject(eval_obj, depsgraph)

    #generate points
    coords = np.empty((n, 3))
    for i in range(n):
        while True:
            point = Vector(random_points_bbox(obj, Rng, 1).flatten())
            if is_point_inside(point, bvh):
                coords[i] = np.array(point)
                break

    return coords


#%%registration
def register():
    pass
def unregister():
    pass