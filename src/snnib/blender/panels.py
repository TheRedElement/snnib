"""
"""


#%%imports
import bpy

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from . import bl_info

#%%definitions
class SNNIB_PT_Panel(bpy.types.Panel):
    """panel hosting the add-on
    """
    bl_label = bl_info["name"]
    bl_idname = "panel.snnib"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = bl_info["name"]

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # #global header        
        # layout.label(text="Generate a Spiking Neural Network")

        #sections
        box = layout.box()
        box.row().label(text="Actions")
        box1 = box.box()
        box1.row().label(text="Initializations (Run Once in Sequence)")
        box1.row().column(align=True).operator("operator.snnib_init_shader_nodes")
        box1.row().column(align=True).operator("operator.snnib_init_geo_nodes")
        box2 = box.box()
        box2.row().label(text="Building")
        box2.row().column(align=True).operator("operator.snnib_make_template_neuron")
        box2.row().column(align=True).operator("operator.snnib_build_snn")
        
        box = layout.box()
        box.row().label(text="Settings")
        box1 = box.box()
        box1.row().label(text="General Settings")
        box1.row().prop(context.scene.snnib_props, "network_container")
        box1.row().prop(context.scene.snnib_props, "template_neuron")
        box1.separator()
        box1.row().label(text="Axons")
        box1.row().prop(context.scene.snnib_props, "axon_length")
        layout.separator()
        
        box2 = box.box()
        box2.row().label(text="Random Network")
        box2.row().prop(context.scene.snnib_props, "seed")
        row = box2.row()
        row.column().prop(context.scene.snnib_props, "n_neurons")
        row.column().prop(context.scene.snnib_props, "p_spike")
        row.column().prop(context.scene.snnib_props, "p_synapses")
        layout.separator()        
        
        box3 = box.box()
        box3.row().label(text="Network from File")
        box3.row().prop(context.scene.snnib_props, "network_file")
        layout.separator()
        


#%%registration
classes = (
    SNNIB_PT_Panel,
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