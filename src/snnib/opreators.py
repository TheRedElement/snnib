"""
"""


#%%imports
import bpy
import bmesh

import logging
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, force=True)

from . import utils
from . import network
from . import DEV

#%%definitions
class SNNIB_OT_build_snn(bpy.types.Operator):
    """operator to build a SNN
    """
    bl_idname = "operator.snnib_build_snn"
    bl_label = "Build SNN"

    def execute(self, context):
        
        #init network
        neurons = None
        synapses = None
        Net = network.Network(
            neurons=neurons,
            synapses=synapses,
        )
        Net.setup_container()
        Net.draw_neurons(
            template_obj=bpy.context.scene.template_neuron
        )
        Net.draw_synapses()
        
        return {'FINISHED'}

class SNNIB_OT_make_template_neuron(bpy.types.Operator):
    """operator to create a template neuron
    """
    bl_idname = "operator.snnib_make_template_neuron"
    bl_label = "Make a Template Neuron"


    def execute(self, context):
        name = "SNNIB.Neuron.Template"
        
        if DEV:
            if name in bpy.data.objects.keys():
                logger.debug("using existing object")
                neuron_obj = bpy.data.objects[name]
            else:
                logger.debug("generating new object")
                network.generate_template_neuron(name)
        else:
            #create sphere (name will be adjusted automatically)
            network.generate_template_neuron(name)    
        
        #other settings
        neuron_obj.hide_render = True
        
        return {'FINISHED'}


#%%registration
classes = (
    SNNIB_OT_build_snn,
    SNNIB_OT_make_template_neuron,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass