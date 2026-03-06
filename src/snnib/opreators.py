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
        
        name = "SNNIB.Neuron.Template"
        if DEV:
            if name in bpy.data.objects.keys():
                logger.debug("using existing object")
                neuron_obj = bpy.data.objects[name]
            else:
                logger.debug("generating new object")
                #create sphere
                bpy.ops.mesh.primitive_cube_add(
                    size=1,
                    location=(0, 0, 0),
                )
                neuron_obj = bpy.context.active_object
                neuron_obj.name = name
                neuron_obj.data.name = name

                #convert to sphere
                radius = .5
                bm = bmesh.new()
                bm.from_mesh(neuron_obj.data)
                bmesh.ops.subdivide_edges(  #subdivide
                    bm,
                    edges=bm.edges,
                    cuts=5,
                    use_grid_fill=True,
                )
                for v in bm.verts:          #convert to sphere (all vertices at constant radius from object origin)
                    v.co = v.co.normalized() * radius
                
                bm.to_mesh(neuron_obj.data)
                bm.free()
        else:
                #create sphere (name will be adjusted automatically)
                bpy.ops.mesh.primitive_cube_add(
                    size=1,
                    location=(0, 0, 0),
                )
                neuron_obj = bpy.context.active_object
                neuron_obj.name = name
                neuron_obj.data.name = name
        
        #add geonodes
        gn = neuron_obj.modifiers.new(name="Neuron.Axon", type='NODES')
        gn.node_group = bpy.data.node_groups["SnnibNeuronNeurites"]
        
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