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
        box.row().label(text="General Settings")
        box.row().prop(scene, "network_container", text="Network container")
        box.row().prop(scene, "template_neuron", text="Template neuron")        
        box.separator()
        box.row().label(text="Axons")
        box.row().prop(context.scene.snnib_props, "axon_length")
        layout.separator()
        
        box = layout.box()
        box.row().label(text="Random network")
        box.row().prop(context.scene.snnib_props, "seed")
        row = box.row()
        row.column().prop(context.scene.snnib_props, "n_neurons")
        row.column().prop(context.scene.snnib_props, "p_spike")
        row.column().prop(context.scene.snnib_props, "p_synapses")
        layout.separator()        
        
        box = layout.box()
        box.row().label(text="Network from file")
        box.row().label(text="TODO: input")
        layout.separator()
        
        layout.row().label(text="Actions")
        layout.row().column(align=True).operator("operator.snnib_build_snn")
        layout.row().column(align=True).operator("operator.snnib_make_template_neuron")
        

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