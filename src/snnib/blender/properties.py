"""defines custom properties used by `SNNIB`

- also defines custom objects

Exceptions

Classes
    - `SnnibProperties` -- custom properties of `SNNIB`

Functions

Other Objects
"""

#%%imports
import bpy

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

#%%definitions
class SnnibProperties(bpy.types.PropertyGroup):
    """custom properties used in `SNNIB`

    Attributes

    Inferred Attributes

    Methods

    Dependencies
        - `bpy`
        - `logging`
    """

    axon_length: bpy.props.FloatProperty(
        name="Axon Length",
        description="Length of the axon in meters. Serves as branching point for connections to other neurons.",
        default=2.0,
        min=0,
        step=0.1,
    )
    n_neurons: bpy.props.IntProperty(
        name="Number of Neurons",
        description="Number of neurons to visualize when generating a random network.",
        default=5,
        min=0,
    )
    network_container: bpy.props.PointerProperty(
        name="Network Container",
        description="Object that will contain the generated network. Objects bounding box defines network boundaries.",
        type=bpy.types.Object,
    )
    network_file: bpy.props.StringProperty(
        name="Network File",
        description="File containing the network to visualize. Will override all properties set in `Random Network` if provided.",
        subtype='FILE_PATH'
    )
    p_spike: bpy.props.FloatProperty(
        name="Spike Probability",
        description="Probability of a spike occurring at any frame when generating a random network. Checked for every neuron individually.",
        default=0.1,
        min=0,
        max=1.0,
        step=0.01,
    )    
    p_synapses: bpy.props.FloatProperty(
        name="Synapse Connection Probability",
        description="Probability that a synapse is connecting two neurons when generating a random network.",
        default=0.5,
        min=0.0,
        max=1.0,
        step=0.01,
    )
    seed: bpy.props.IntProperty(
        name="Random Seed",
        description="Random seed.",
        default=0,
        min=0,
    )
    template_neuron: bpy.props.PointerProperty(
        name="Template Neuron",
        description="Template instance that will be used as neurons in the visulaized network. It is recommended to generate a template neuron using `Make a Template Neuron` as preset geometry nodes allow for easy customization downstream.",
        type=bpy.types.Object,
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
    del bpy.types.Scene.template_neuron
    del bpy.types.Scene.network_container