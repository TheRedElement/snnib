#%%imports
import bpy

import numpy as np

#%%definitions
class BsnnProperties(bpy.types.PropertyGroup):
    """custom properties used in the UI
    """
    
    n_neurons: bpy.props.IntProperty(
        name="Number of Neurons",
        default=10,
        min=0,
    )
    p_synapses: bpy.props.FloatProperty(
        name="Synapse Connection Probability",
        default=0.5,
        min=0.0,
        max=1.0,
        step=0.01,
    )
    seed: bpy.props.IntProperty(
        name="Random Seed",
        default=0,
        min=0,
    )

#%%registring
classes = (
    BsnnProperties,
)

def register():
    bpy.utils.register_class(BsnnProperties)
    bpy.types.Scene.bsnn_props = bpy.props.PointerProperty(type=BsnnProperties)    

def unregister():
    bpy.utils.unregister_class(BsnnProperties)
    del bpy.types.Scene.bsnn_props
