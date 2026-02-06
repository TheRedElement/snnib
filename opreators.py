"""
"""


#%%imports
import bpy

import logging
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from . import utils
from . import network

#%%definitions
class SNNIB_OT_build(bpy.types.Operator):
    """operator to build a SNN
    """
    bl_idname = "operator.snnib_build"
    bl_label = "Build SNN"

    def execute(self, context):
        
        #DEV: clear container children
        logger.warning(f"DEV: clearing children of network container")
        for child in bpy.context.scene.network_container.children_recursive:
            bpy.data.objects.remove(child, do_unlink=True)
                        
        #init network
        coords = None
        synapses = None
        Net = network.Network(
            coords=coords,
            synapses=synapses,
        )
        Net.draw_neurons(
            template_obj=bpy.context.scene.template_neuron
        )
        Net.draw_synapses()
        
        return {'FINISHED'}



#%%registration
classes = (
    SNNIB_OT_build,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)