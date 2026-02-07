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

class SNNIB_OT_make_template_neuron(bpy.types.Operator):
    """operator to create a template neuron
    """
    bl_idname = "operator.snnib_make_template_neuron"
    bl_label = "Make a Template Neuron"

    def execute(self, context):
        
        #DEV: clear container children
        logger.debug(f"building template neuron")
         
        """TODO: uncomment once geonodes defined
        #remove if existent
        obj = bpy.data.objects.get("SNNIB.Neuron.Template")
        if obj is not None:
            mesh = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.meshes.remove(mesh)
         
        #create sphere               
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=1,
            location=(0, 0, 0),
            segments=9,
            ring_count=5,
        )
        neuron_obj = bpy.context.active_object
        neuron_obj.name = "SNNIB.Neuron.Template"
        neuron_obj.data.name = "SNNIB.Neuron.Template"
        
        #add geonodes
        gn = neuron_obj.modifiers.new(name="Neuron_Axon", type='NODES')
        gn.node_group = bpy.data.node_groups.new("Neuron_Axon", 'GeometryNodeTree')
        node_group = gn.node_group
        """
        
        
        #DEV: get existing elements
        neuron_obj = bpy.data.objects.get("SNNIB.Neuron.Template")
        gn = neuron_obj.modifiers.get("Neuron_Axon")
        node_group = gn.node_group
        
        """
        ##define interface
        geo_in = node_group.interface.new_socket(
            name="Neuron Object",
            description="Neuron",
            in_out='INPUT',
            socket_type='NodeSocketGeometry'
        )
        scale_in = node_group.interface.new_socket(
            name="Axon Curve",
            description="Curve representing the neurons axon",
            in_out='INPUT',
            socket_type='NodeSocketObject'
        )
        geo_out = node_group.interface.new_socket(
            name="Neuron",
            description="Neuron inluding axon",
            in_out='OUTPUT',
            socket_type='NodeSocketGeometry'
        )
        """
        
        
        ##add nodes
        n_group_input_1 = node_group.nodes.new(type="NodeGroupInput")
        n_group_input_1.location = (000, 100)
        n_group_output_1 = node_group.nodes.new(type="NodeGroupOutput")
        n_group_output_1.location = (1000, 0)
        
        ###neuron
        frame_n = node_group.nodes.new(type="NodeFrame")
        frame_n.label = "Neuron"
        frame_n.location = (0,0)
        
        n_bsnn_pos_glob1 = node_group.nodes.new(type="GeometryNodeGroup")
        n_bsnn_pos_glob1.node_tree = bpy.data.node_groups["BsnnPositionGlobal"]
        n_bsnn_pos_glob1.location = (200, 000)
        n_bsnn_pos_glob1.parent = frame_n

        n_noise_tex1 = node_group.nodes.new(type="ShaderNodeTexNoise")
        n_noise_tex1.location = (400, 000)
        n_noise_tex1.parent = frame_n

        n_m_mult1 = node_group.nodes.new(type="ShaderNodeMath")
        n_m_mult1.operation = "MULTIPLY"
        n_m_mult1.location = (600, 000)
        n_m_mult1.parent = frame_n        

        n_bsnn_scale_rad1 = node_group.nodes.new(type="GeometryNodeGroup")
        n_bsnn_scale_rad1.node_tree = bpy.data.node_groups["BsnnScaleRadial"]
        n_bsnn_scale_rad1.location = (800, 000)
        n_bsnn_scale_rad1.parent = frame_n        


        ##add links
        node_group.links.new(n_group_input_1.outputs["Neuron Object"], n_bsnn_scale_rad1.inputs[0])
        node_group.links.new(n_bsnn_scale_rad1.outputs["Geometry"], n_group_output_1.inputs[0])
        node_group.links.new(n_bsnn_pos_glob1.outputs["Global Position"], n_noise_tex1.inputs[0])
        node_group.links.new(n_noise_tex1.outputs["Color"], n_m_mult1.inputs[0])
        node_group.links.new(n_m_mult1.outputs["Value"], n_bsnn_scale_rad1.inputs[1])
        
        
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