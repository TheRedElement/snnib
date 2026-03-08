"""
"""


#%%imports
import bpy
import bmesh

import logging
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, force=True)

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
        
        #get inputs from ui
        if bpy.context.scene.snnib_props.network_container is None:
            network_container = bpy.context.active_object
        else:
            network_container = bpy.context.scene.snnib_props.network_container
        if bpy.context.scene.snnib_props.template_neuron is None:
            template_neuron = network.generate_template_neuron("SNNIB.Neuron.Template")
            template_neuron.parent = network_container          
        else:
            template_neuron = bpy.context.scene.snnib_props.template_neuron
        
        #init network
        Net = network.Network(
            network_container=network_container,
            template_neuron=template_neuron,
            network_file=bpy.context.scene.snnib_props.network_file,
        )
        Net.setup_container()
        Net.draw_neurons()
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
                neuron_obj = network.generate_template_neuron(name)
        else:
            #create sphere (name will be adjusted automatically)
            neuron_obj = network.generate_template_neuron(name)    
        
        #other settings
        neuron_obj.hide_render = True
        
        return {'FINISHED'}

class SNNIB_OT_init_geo_nodes(bpy.types.Operator):
    """initializes all geometry nodes node trees needed for the add-on to work
    """
    bl_idname = "operator.snnib_init_geo_nodes"
    bl_label = "Initialize SNNIB Geometry Nodes"

    def execute(self, context):
        from . import geo_nodes
        from . import shader_nodes

        shader_nodes.register() #NOTE: needs to register first because used in `geo_nodes`!
        geo_nodes.register()

        return {'FINISHED'}

class SNNIB_OT_init_shader_nodes(bpy.types.Operator):
    """initializes all shader nodes node trees needed for the add-on to work
    """
    bl_idname = "operator.snnib_init_shader_nodes"
    bl_label = "Initialize SNNIB Shader Nodes"

    def execute(self, context):
        from . import shader_nodes

        shader_nodes.register()

        return {'FINISHED'}

#%%registration
classes = (
    SNNIB_OT_build_snn,
    SNNIB_OT_init_geo_nodes,
    SNNIB_OT_init_shader_nodes,
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