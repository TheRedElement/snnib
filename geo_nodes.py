"""custom geo node node groups

- naming pattern: Snnib<Name>
"""

import bpy
from bpy.types import Node, NodeSocket
from bpy.props import FloatProperty

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from . import utils
  
def position_global():
    """creates a geometry nodes node group that returns position in global coordinates

    - useful for defining one GeoNodes modifier and applying it to different objects scattered throughout the scene
        - i.e., small random variations in each neuron
    """

    #group attributes    
    group_name = "SnnibPositionGlobal"

    #delete if already existent
    utils.geo_nodes_utils.delete_geonode_groups(group_name)

    #new node group
    node_group = bpy.data.node_groups.new(name=group_name, type='GeometryNodeTree')

    #define interface
    global_position_out = node_group.interface.new_socket(
        name="Global Position",
        description="objects position in the global coordinate system",
        in_out='OUTPUT',
        socket_type='NodeSocketVector'
    )

    #add nodes
    n_self_object_1 = node_group.nodes.new(type="GeometryNodeSelfObject")
    n_self_object_1.location = (0, 0)
    
    n_obj_info_1 = node_group.nodes.new(type="GeometryNodeObjectInfo")
    n_obj_info_1.location = (200, 0)

    n_position_1 = node_group.nodes.new(type="GeometryNodeInputPosition")
    n_position_1.location = (200, -300)
    
    n_vector_math_add_1 = node_group.nodes.new(type="ShaderNodeVectorMath")
    n_vector_math_add_1.operation = 'ADD'
    n_vector_math_add_1.location = (400, 0)
    
    n_group_output_1 = node_group.nodes.new(type="NodeGroupOutput")
    n_group_output_1.location = (600, 0)
    
    #add connections
    node_group.links.new(n_self_object_1.outputs["Self Object"], n_obj_info_1.inputs[0])
    node_group.links.new(n_obj_info_1.outputs["Location"], n_vector_math_add_1.inputs[0])
    node_group.links.new(n_position_1.outputs["Position"], n_vector_math_add_1.inputs[1])
    node_group.links.new(n_vector_math_add_1.outputs[0], n_group_output_1.inputs[0])

    return
    
def scale_radial():
    """creates a geometry nodes node group that scales input geometry radially
    """

    #group attributes    
    group_name = "SnnibScaleRadial"

    #delete if already existent
    utils.geo_nodes_utils.delete_geonode_groups(group_name)

    #new node group
    node_group = bpy.data.node_groups.new(name=group_name, type='GeometryNodeTree')

    #define interface
    geo_in = node_group.interface.new_socket(
        name="Geometry",
        description="geometry to be scaled in radial direction",
        in_out='INPUT',
        socket_type='NodeSocketGeometry'
    )
    scale_in = node_group.interface.new_socket(
        name="Scale",
        description="vector (or texture) to use for scaling",
        in_out='INPUT',
        socket_type='NodeSocketVector'
    )
    geo_out = node_group.interface.new_socket(
        name="Geometry",
        description="geometry after being scaled radially",
        in_out='OUTPUT',
        socket_type='NodeSocketGeometry'
    )


    #add nodes
    n_group_input_1 = node_group.nodes.new(type="NodeGroupInput")
    n_group_input_1.location = (000, 100)
    
    n_position_1 = node_group.nodes.new(type="GeometryNodeInputPosition")
    n_position_1.location = (200, 0)
    
    n_vector_math_norm_1 = node_group.nodes.new(type="ShaderNodeVectorMath")
    n_vector_math_norm_1.operation = 'NORMALIZE'
    n_vector_math_norm_1.location = (400, 0)
            
    n_vector_math_mult_1 = node_group.nodes.new(type="ShaderNodeVectorMath")
    n_vector_math_mult_1.operation = 'MULTIPLY'
    n_vector_math_mult_1.location = (600, 0)
    
    n_set_position_1 = node_group.nodes.new(type="GeometryNodeSetPosition")
    n_set_position_1.location = (800, 0)    
    
    n_group_output_1 = node_group.nodes.new(type="NodeGroupOutput")
    n_group_output_1.location = (1000, 0)
    
    #add connections
    node_group.links.new(n_group_input_1.outputs["Geometry"], n_set_position_1.inputs[0])
    node_group.links.new(n_group_input_1.outputs["Scale"], n_vector_math_mult_1.inputs[1])
    node_group.links.new(n_position_1.outputs["Position"], n_vector_math_norm_1.inputs[0])
    node_group.links.new(n_vector_math_norm_1.outputs["Vector"], n_vector_math_mult_1.inputs[0])
    node_group.links.new(n_vector_math_mult_1.outputs["Vector"], n_set_position_1.inputs[3])
    node_group.links.new(n_set_position_1.outputs["Geometry"], n_group_output_1.inputs[0])


#%%registration
def register():
    position_global()
    scale_radial()

def unregister():
    pass