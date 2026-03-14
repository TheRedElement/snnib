
"""functions related to spiketrain generation and manipulation

Exceptions

Classes

Functions
    - `make_spike_texture()` -- generates a texture to encode spiketrains

Other Objects
"""

#%%imports
import bpy

import importlib
import logging
import numpy as np
from typing import List

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

# from . import utils


#%%definitions
def make_spike_texture(
    spike_steps:List[int],
    steps:int,
    img_name:str,
    override:bool=False,
    ) -> bpy.types.Image:
    """generates an image representing the spiketrain encoded in `spike_steps`

    - will
        - create an image with `height=1` and `width=steps`
    - image pixels are either white (spike) or black (no spike)
    
    Parameters
        - `spike_steps`
            - `List[int]`
            - indices of the simulation steps where a spike occurred
            - spiketrain converted to a step-encoding rather than actual spike times
            - the generated image will have a white pixel at each pixel that is contained in `spike_steps`
        - `steps`
            - `int`
            - total simulation converted to steps (rather than time)
            - equivalent to $t_{sim} / dt$
                - $t_{sim}$ ...  total simulation time
                - $dt$ ...  simulation time step
        - `img_name`
            - `str`
            - name to give to the generated image
        - `override`
            - `bool`, optional
            - whether to override an existing image rather than creating a new one
            - if `True`
                - will override an existing image and generate a new one if no image was existing prior to function call
            - if `False`
                - will generate a new image regardless of prior existence
                - recommended because different image shapes can lead to issues
            - the default is `False`

    Raises

    Returns
        - ìmg`
            - `bpy.types.Image`
            - the generated image

    Dependencies
        - `bpy`
        - `logging`
        - `numpy`
        - `typing`
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
