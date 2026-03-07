#%%imports
import bpy


#%%definitions
class SnnibProperties(bpy.types.PropertyGroup):
    """custom properties used in the UI
    """

    axon_length: bpy.props.FloatProperty(
        name="Axon Length",
        default=3,
        min=0,
        step=0.1,
    )
    n_neurons: bpy.props.IntProperty(
        name="Number of Neurons",
        default=5,
        min=0,
    )    
    p_spike: bpy.props.FloatProperty(
        name="Spike Probability",
        default=0.1,
        min=0,
        max=1.0,
        step=0.01,
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
    synapse_max_nonconnections: bpy.props.IntProperty(
        name="Maximum Number of Synapse Non-Connections",
        default=3,
        min=0,
    )
    synapse_maxlen_nonconnections: bpy.props.FloatProperty(
        name="Maximum Length of Synapse Non-Connection",
        default=3,
        min=0,
        step=0.1,
    )    
    synapse_resolution: bpy.props.IntProperty(
        name="Synapse Resolution",
        default=4,
        min=4,
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
    try:
        bpy.utils.unregister_class(SnnibProperties)
    except:
        pass
    del bpy.types.Scene.snnib_props

    #custom objects
    del bpy.types.Scene.network_container