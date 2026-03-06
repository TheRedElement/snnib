"""development script

- loads and unloads `snnib`
- used to test basic functions outside the package
"""

#%%imports

import bpy

import importlib
import logging
import numpy as np
import sys

#add paths
if bpy.path.abspath("//") not in sys.path:
    sys.path.append(bpy.path.abspath("//"))
for p in sys.path:
    print(p)

###############
#import add-on#
###############
from src import snnib


logger = logging.getLogger(__name__)

#reload libraries
importlib.reload(snnib)
#importlib.reload(snnib.utils.random)
# snnib.geo_nodes.neuron_axon()

#%%constants


#%%definitions
def make_spike_texture(
    spike_times,
    img_name:str,
    override:bool=True,
    ):
    import numpy as np

    #global settings
    scene = bpy.context.scene
    frame_start = scene.frame_start
    frame_end = scene.frame_end
    n_frames = frame_end - frame_start + 1
    
    #override current image if requested
    if override and img_name in bpy.data.images.keys():
        img = bpy.data.images[img_name]  #get image
        # img.user_clear()                #clear users
        # if not img.users:
        #     bpy.data.images.remove(img) #delete
    else:
        #create new image (with new name)
        img = bpy.data.images.new(
            name=img_name,
            width=n_frames,
            height=1,
            alpha=True,
        )
        img.generated_type = 'BLANK'


    #get image width and height
    w, h = img.size
    pixels = np.zeros((h, w, 4))
    pixels[:,:,3] = 1.0

    for t in spike_times:
        print(t, w)
        if t < w:
            pixels[:,t,:] = 1.0
        else:
            logger.warning(f"spiketime {t} >= image width ({w})... ignoring")

    img.pixels = pixels.flatten()

    img.update()
    
    return

#NOTE: execute twice to make changes in submodules visible!!!
if __name__ == "__main__":
    spiketimes_main1 = np.array([00, 30, 60, 90, 120])
    # spiketimes_main2 = np.array([15, 45, 60, 90, 120])
    # spiketimes_main3 = np.array([75, 105])
    # make_spike_texture(spiketimes_main1, img_name="SpikeTrain.Main.001", override=True)
    # make_spike_texture(spiketimes_main2, img_name="SpikeTrain.Main.002", override=True)
    # make_spike_texture(spiketimes_main3, img_name="SpikeTrain.Main.003", override=True)
    
    try:
        snnib.unregister()
    finally:
        snnib.register()
