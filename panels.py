"""
"""


#%%imports
import bpy

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from . import bl_info
# from blend_snn import bl_info

#%%definitions
class BSNN_PT_Panel(bpy.types.Panel):
    """panel hosting the add-on
    """
    bl_label = bl_info["name"]
    bl_idname = "panel.bsnn"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = bl_info["name"]

    def draw(self, context):
        layout = self.layout

        layout.label(text="Generate a Spiking Neural Network")

        layout.separator()

        col = layout.column(align=True)
        #col.operator("wm.open_mainfile", text="Open File")
        scene = context.scene
        col.prop(scene, "template_neuron", text="Template Neuron")
        
        layout.separator()

        row = layout.row()
        row.operator("operator.bsnn_build")


#%%registration
classes = (
    BSNN_PT_Panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)