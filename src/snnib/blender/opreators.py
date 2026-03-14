"""operators used within the [blender](https://www.blender.org/) UI

- defines and registers various operators that can be used to generate a `SNNIB` network

Exceptions
    - `SNNIB_OT_build_snn` -- operator to build a `SNNIB` network
    - `SNNIB_OT_make_template_neuron` -- operator to generate a template neuron
    - `SNNIB_OT_init_geo_nodes` -- operator to initialize the geo nodes node trees needed in `SNNIB`
    - `SNNIB_OT_init_shader_nodes` -- operator to initialize the shader nodes node trees needed in `SNNIB`

Classes

Functions

Other Objects
"""


#%%imports
import bpy

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, force=True)

from . import network
from . import DEV

#%%definitions
class SNNIB_OT_build_snn(bpy.types.Operator):
    """operator to build a SNN with the current user settings

    - see `self.execute()`

    Attributes

    Inferred Attributes

    Methods
        - `execute()`

    Dependencies
        - `bpy`
        - `logging`
    """

    bl_idname = "operator.snnib_build_snn"
    bl_label = "Build SNN"

    def execute(self, context):
        """builds the `SNNIB` network

        - called whenever the respective button is clicked
        - will
            - read the input specified in the UI panel
                - `network_container`
                - `template_neuron`
                - `network_file`
            - initialize a `network.Network`
            - setup the container
            - draw the neurons
            - draw the synapses
        
        Parameters
            - `context`
                - the current context
                - not used

        Raises

        Returns
            - `{'FINISHED'}`
        """
        
        #catching errors
        if bpy.context.scene.snnib_props.network_container is None:
            self.report({'ERROR'}, "`Network Container` required")
            return {'CANCELLED'}
        if bpy.context.scene.snnib_props.template_neuron is None:
            self.report({'ERROR'}, "`Template Neuron` required")
            return {'CANCELLED'}
        if bpy.context.scene.snnib_props.network_file in [None,""]:
            self.report({'INFO'}, "generating random network (no `Network File` provided)")
        else:
            self.report({'INFO'}, "using `Network File` to generate network instead of `Random Network` settings")

        #get inputs from ui
        network_container = bpy.context.scene.snnib_props.network_container
        template_neuron = bpy.context.scene.snnib_props.template_neuron
        network_file = bpy.context.scene.snnib_props.network_file
        
        #init network
        Net = network.Network(
            network_container=network_container,
            template_neuron=template_neuron,
            network_file=network_file,
        )
        Net.setup_container()
        Net.draw_neurons()
        Net.draw_synapses()
        
        return {'FINISHED'}

class SNNIB_OT_init_geo_nodes(bpy.types.Operator):
    """initializes all geometry nodes node trees needed for the add-on to work
    
    - see `self.execute()`

    Attributes

    Inferred Attributes

    Methods
        - `execute()`

    Dependencies
        - `bpy`
        - `logging`    
    """

    bl_idname = "operator.snnib_init_geo_nodes"
    bl_label = "Initialize SNNIB Geometry Nodes"

    def execute(self, context):
        """creates geo nodes node trees needed for `SNNIB`

        - will also register the shader nodes
            - geo nodes use the shader nodes internally
        
        Parameters
            - `context`
                - the current context
                - not used

        Raises

        Returns
            - `{'FINISHED'}`        
        """
        from . import geo_nodes
        from . import shader_nodes

        shader_nodes.register() #NOTE: needs to register first because used in `geo_nodes`!
        geo_nodes.register()

        return {'FINISHED'}

class SNNIB_OT_init_shader_nodes(bpy.types.Operator):
    """initializes all shader nodes node trees needed for the add-on to work
    
    - see `self.execute()`

    Attributes

    Inferred Attributes

    Methods
        - `execute()`

    Dependencies
        - `bpy`
        - `logging`
    """

    bl_idname = "operator.snnib_init_shader_nodes"
    bl_label = "Initialize SNNIB Shader Nodes"

    def execute(self, context):
        """creates shader nodes node trees needed for `SNNIB`
        
        Parameters
            - `context`
                - the current context
                - not used

        Raises

        Returns
            - `{'FINISHED'}`        
        """        
        from . import shader_nodes

        shader_nodes.register()

        return {'FINISHED'}

class SNNIB_OT_make_template_neuron(bpy.types.Operator):
    """operator to create a template neuron
    
    - see `self.execute()`

    Attributes

    Inferred Attributes

    Methods
        - `execute()`

    Dependencies
        - `bpy`
        - `logging`
    """

    bl_idname = "operator.snnib_make_template_neuron"
    bl_label = "Make a Template Neuron"


    def execute(self, context):
        """creates template neuron

        Parameters
            - `context`
                - the current context
                - not used

        Raises

        Returns
            - `{'FINISHED'}`          
        """
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