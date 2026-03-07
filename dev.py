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

#NOTE: execute twice to make changes in submodules visible!!!
if __name__ == "__main__":
   
    try:
        snnib.unregister()
    finally:
        snnib.register()
