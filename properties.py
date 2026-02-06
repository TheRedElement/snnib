#%%imports
import bpy


#%%definitions
class SnnibProperties(bpy.types.PropertyGroup):
    """custom properties used in the UI
    """

    axon_branching_factor: bpy.props.IntProperty(
        name="Axon Branching Factor",
        default=3,
        min=0,
        step=1,
    )
    axon_length: bpy.props.FloatProperty(
        name="Axon Length",
        default=3,
        min=0,
        step=0.1,
    )
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
    voxel_size: bpy.props.FloatProperty(
        name="Voxel Size",
        default=0.1,    #m
        min=0,
    )

#%%registring
classes = (
    SnnibProperties,
)

def register():
    bpy.utils.register_class(SnnibProperties)
    bpy.types.Scene.snnib_props = bpy.props.PointerProperty(type=SnnibProperties)    

    #custom objects
    bpy.types.Scene.template_neuron = bpy.props.PointerProperty(
        name="Template Neuron",
        type=bpy.types.Object
    )
    bpy.types.Scene.network_container = bpy.props.PointerProperty(
        name="Network Container",
        type=bpy.types.Object
    )


def unregister():
    bpy.utils.unregister_class(SnnibProperties)
    del bpy.types.Scene.snnib_props

    #custom objects
    del bpy.types.Scene.network_container