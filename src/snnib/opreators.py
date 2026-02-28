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
class SNNIB_OT_build_snn(bpy.types.Operator):
    """operator to build a SNN
    """
    bl_idname = "operator.snnib_build_snn"
    bl_label = "Build SNN"

    def execute(self, context):
        
        #init network
        coords = None
        synapses = None
        Net = network.Network(
            coords=coords,
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
        
        #DEV: clear container children
        logger.debug(f"building template neuron")
         
        """
        #remove if existent
        obj = bpy.data.objects.get("SNNIB.Neuron.Template")
        if obj is not None:
            mesh = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.meshes.remove(mesh)
        """
        
        #create sphere
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=1,
            location=(0, 0, 0),
            segments=18,
            ring_count=9,
        )
        neuron_obj = bpy.context.active_object
        neuron_obj.name = "SNNIB.Neuron.Template"
        neuron_obj.data.name = "SNNIB.Neuron.Template"
        
        #add geonodes
        gn = neuron_obj.modifiers.new(name="Neuron.Axon", type='NODES')
        gn.node_group = bpy.data.node_groups["SnnibNeuronAxon"]
        
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
        bpy.utils.unregister_class(cls)