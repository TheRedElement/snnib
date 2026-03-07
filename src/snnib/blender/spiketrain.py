
"""
"""

#%%imports
import bpy
import bmesh

import importlib
import logging
import numpy as np
from typing import List

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

from . import utils


#%%definitions
def make_spike_texture(
    spike_steps:List[int],
    steps:int,
    img_name:str,
    override:bool=True,
    ) -> bpy.types.Image:
    """generates an image representing the spiketrain encoded in `spiketimes` 
    """
    
    #override current image if requested
    if override and img_name in bpy.data.images.keys():
        img = bpy.data.images[img_name]     #get image
        # img.user_clear()                    #clear users
        # if not img.users:
        #     bpy.data.images.remove(img)     #delete
    else:
        #create new image (with new name)
        img = bpy.data.images.new(
            name=img_name,
            width=steps,            #every step is a single pixel
            height=1,
            alpha=True,
        )
        img.generated_type = 'BLANK'


    #get image width and height
    w, h = img.size
    pixels = np.zeros((h, w, 4))
    pixels[:,:,3] = 1.0

    for t in spike_steps:
        if t < w:
            pixels[:,t,:] = 1.0
        else:
            logger.warning(f"spiketime {t} >= image width ({w})... ignoring")

    img.pixels = pixels.flatten()

    img.update()
    
    return img