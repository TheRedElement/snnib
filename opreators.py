"""
"""


#%%imports
import bpy

import logging
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from . import utils
from . import blend_snn

#%%definitions
class BSNN_OT_build(bpy.types.Operator):
    """operator to build a SNN
    """
    bl_idname = "operator.bsnn_build"
    bl_label = "Build SNN"

    def execute(self, context):
        
        
        bsnn_collection = utils.collection_utils.ensure_collection("BSNN")
        utils.collection_utils.clear_collection(bsnn_collection)   #make sure collection is clean for testing
        
        #generate neurons at random locations
        times = np.arange(0,120,1)
        coords = (np.random.rand(10,3) - 0.5) * 10

        #generate random synapses
        synapses = np.random.rand(coords.shape[0],coords.shape[0]).round(decimals=1)
        synapses *= (np.random.rand(*synapses.shape) > 0.8)
        connected = (synapses > 0)
        np.transpose(synapses.nonzero())
        synapses = np.append(np.transpose(np.where(connected)), synapses[connected].reshape(-1,1), axis=1)
        
        #init network
        Net = blend_snn.Network(
            bsnn_collection=bsnn_collection,
            times=times,
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
    BSNN_OT_build,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)