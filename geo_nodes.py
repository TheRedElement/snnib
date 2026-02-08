"""custom geo node node groups

- naming pattern: Snnib<Name>


TODO:
    - neuron_axon():
        - add set_shade_smooth
        - add_smooth_geometry
"""

#%%imports
import bpy
from bpy.types import Node, NodeSocket
from bpy.props import FloatProperty

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from . import utils
  
#%%definitions

def network_container():
    """creates a geometry nodes node group to style the network container
    
    - converts to wireframe
    """

    #group attributes    
    group_name = "SnnibNetworkContainer"

    #delete if already existent
    utils.geo_nodes_utils.delete_geonode_groups(group_name)

    #new node group
    node_group = bpy.data.node_groups.new(name=group_name, type='GeometryNodeTree')

    #define interface
    geo_in = node_group.interface.new_socket(
        name="Network Container",
        description="Container of the network",
        in_out='INPUT',
        socket_type='NodeSocketGeometry'
    )
    geo_out = node_group.interface.new_socket(
        name="Network Container",
        description="Container of the network",
        in_out='OUTPUT',
        socket_type='NodeSocketGeometry'
    )

    ##add nodes
    n_group_input_1 = node_group.nodes.new(type="NodeGroupInput")
    n_group_input_1.location = (000, 100)
    n_group_output_1 = node_group.nodes.new(type="NodeGroupOutput")
    n_group_output_1.location = (400, 0)

    n_mesh2curve = node_group.nodes.new(type="GeometryNodeMeshToCurve")
    n_mesh2curve.location = (200, 0)
    
    #add connections
    node_group.links.new(n_group_input_1.outputs["Network Container"], n_mesh2curve.inputs["Mesh"])
    node_group.links.new(n_mesh2curve.outputs["Curve"], n_group_output_1.inputs[0])

    return

def neuron_axon():
    """creates template geonodes node group for defining neurons and axons
    
    - this group is used to make created networks customizable in an intuitive manner 
    """
    
    #group attributes    
    group_name = "SnnibNeuronAxon"

    #delete if already existent
    utils.geo_nodes_utils.delete_geonode_groups(group_name)

    #new node group
    node_group = bpy.data.node_groups.new(name=group_name, type='GeometryNodeTree')    
    
    ##define interface
    neuron_in = node_group.interface.new_socket(
        name="Neuron Object",
        description="Neuron",
        in_out='INPUT',
        socket_type='NodeSocketGeometry'
    )
    axon_in = node_group.interface.new_socket(
        name="Axon Curve",
        description="Curve representing the neurons axon",
        in_out='INPUT',
        socket_type='NodeSocketObject'
    )
    container_in = node_group.interface.new_socket(
        name="Network Container",
        description="Container of the network",
        in_out='INPUT',
        socket_type='NodeSocketObject'
    )
    container_in = node_group.interface.new_socket(
        name="Neuron Material",
        description="Material of combined neuron  and axon",
        in_out='INPUT',
        socket_type='NodeSocketMaterial'
    )
    neuron_out = node_group.interface.new_socket(
        name="Neuron",
        description="Neuron inluding axon",
        in_out='OUTPUT',
        socket_type='NodeSocketGeometry'
    )

    ##add nodes
    n_group_input_1 = node_group.nodes.new(type="NodeGroupInput")
    n_group_input_1.location = (000, 100)
    n_group_output_1 = node_group.nodes.new(type="NodeGroupOutput")
    n_group_output_1.location = (4200, 0)

    ##control values
    frame_c = node_group.nodes.new(type="NodeFrame")
    frame_c.label = "Controls"
    frame_c.location = (0,0)

    n_neuron_surface_rand = node_group.nodes.new(type="ShaderNodeValue")
    n_neuron_surface_rand.label = "Neuron.SurfaceRandomness"
    n_neuron_surface_rand.location = (000, -100)
    n_neuron_surface_rand.outputs[0].default_value = 0.3
    n_neuron_surface_rand.parent = frame_c

    n_axon_ref_width = node_group.nodes.new(type="ShaderNodeValue")
    n_axon_ref_width.label = "Axon.ReferenceWidth"
    n_axon_ref_width.location = (000, -200)
    n_axon_ref_width.outputs[0].default_value = 0.2
    n_axon_ref_width.parent = frame_c

    n_voxel_size = node_group.nodes.new(type="ShaderNodeValue")
    n_voxel_size.label = "Network.VoxelSize"
    n_voxel_size.location = (000, -300)
    n_voxel_size.outputs[0].default_value = 0.1
    n_voxel_size.parent = frame_c

    n_threshold = node_group.nodes.new(type="ShaderNodeValue")
    n_threshold.label = "Network.VoxelThreshold"
    n_threshold.location = (000, -400)
    n_threshold.outputs[0].default_value = 0.2
    n_threshold.parent = frame_c
    
    n_axon_res = node_group.nodes.new(type="FunctionNodeInputInt")
    n_axon_res.label = "Axon.Resolution"
    n_axon_res.location = (000, -500)
    n_axon_res.integer = 10
    n_axon_res.parent = frame_c
    
    ##global
    n_join_geo = node_group.nodes.new(type="GeometryNodeJoinGeometry")
    n_join_geo.location = (3200, 0)
    
    ##remesh
    xpos_rm = 3400
    frame_rm = node_group.nodes.new(type="NodeFrame")
    frame_rm.label = "Neuron.Remesh"
    frame_rm.location = (0,0)
    
    n_mesh2grid = node_group.nodes.new(type="GeometryNodeMeshToSDFGrid")
    n_mesh2grid.location = (xpos_rm, 0)
    n_mesh2grid.parent = frame_rm
    
    n_voxelize = node_group.nodes.new(type="GeometryNodeGridVoxelize")
    n_voxelize.location = (xpos_rm+200, 0)
    n_voxelize.parent = frame_rm
    
    n_grid2mesh = node_group.nodes.new(type="GeometryNodeGridToMesh")
    n_grid2mesh.location = (xpos_rm+400, 0)
    n_grid2mesh.parent = frame_rm
    
    ##apply material
    n_set_material = node_group.nodes.new(type="GeometryNodeSetMaterial")
    n_set_material.location = (xpos_rm+600, 0)
    
    ########
    #neuron#
    ########
    xpos_n = 1000
    frame_n = node_group.nodes.new(type="NodeFrame")
    frame_n.label = "Neuron"
    frame_n.location = (0,0)

    n_bsnn_pos_glob1 = node_group.nodes.new(type="GeometryNodeGroup")
    n_bsnn_pos_glob1.node_tree = bpy.data.node_groups["BsnnPositionGlobal"]
    n_bsnn_pos_glob1.location = (xpos_n, 000)
    n_bsnn_pos_glob1.parent = frame_n

    n_noise_tex1 = node_group.nodes.new(type="ShaderNodeTexNoise")
    n_noise_tex1.location = (xpos_n + 200, 000)
    n_noise_tex1.noise_dimensions = '4D'
    n_noise_tex1.parent = frame_n

    n_m_mult1 = node_group.nodes.new(type="ShaderNodeMath")
    n_m_mult1.operation = "MULTIPLY"
    n_m_mult1.location = (xpos_n+400, 000)
    n_m_mult1.parent = frame_n        

    n_bsnn_scale_rad1 = node_group.nodes.new(type="GeometryNodeGroup")
    n_bsnn_scale_rad1.node_tree = bpy.data.node_groups["BsnnScaleRadial"]
    n_bsnn_scale_rad1.location = (xpos_n+600, 000)
    n_bsnn_scale_rad1.parent = frame_n        

    #################
    #Axon + Synapses#
    #################
    xpos = 0
    ypos = -500
    frame_s = node_group.nodes.new(type="NodeFrame")
    frame_s.label = "Axon + Synapses"
    frame_s.location = (0,0)

    n_obj_info1 = node_group.nodes.new(type="GeometryNodeObjectInfo")
    n_obj_info1.transform_space = 'RELATIVE'
    n_obj_info1.location = (xpos+200, ypos)
    n_obj_info1.parent = frame_s

    n_res_curve1 = node_group.nodes.new(type="GeometryNodeResampleCurve")
    n_res_curve1.location = (xpos+400, ypos)
    n_res_curve1.parent = frame_s

    #random bends
    frame_s_bends = node_group.nodes.new(type="NodeFrame")
    frame_s_bends.label = "Random Bends"
    frame_s_bends.location = (0,0)
    frame_s_bends.parent = frame_s

    n_noise_tex2 = node_group.nodes.new(type="ShaderNodeTexNoise")
    n_noise_tex2.location = (xpos+600, ypos-200)
    n_noise_tex2.noise_dimensions = '4D'
    n_noise_tex2.parent = frame_s_bends        

    n_map_range2 = node_group.nodes.new(type="ShaderNodeMapRange")
    n_map_range2.location = (xpos+800, ypos-200)
    n_map_range2.inputs["To Min"].default_value = -1.0        
    n_map_range2.parent = frame_s_bends

    n_set_pos1 = node_group.nodes.new(type="GeometryNodeSetPosition")
    n_set_pos1.location = (xpos+1000, ypos-0)
    n_set_pos1.parent = frame_s_bends

    #width scaling
    xpos_ws = xpos+1300
    ypos_ws = ypos - 300
    frame_s_ws = node_group.nodes.new(type="NodeFrame")
    frame_s_ws.label = "Axon Width Scaling"
    frame_s_ws.location = (0,0)
    frame_s_ws.parent = frame_s

    frame_s_bbe = node_group.nodes.new(type="NodeFrame")
    frame_s_bbe.label = "Bounding Box Extrema"
    frame_s_bbe.location = (0,0)
    frame_s_bbe.parent =frame_s_ws

    n_obj_info2 = node_group.nodes.new(type="GeometryNodeObjectInfo")
    n_obj_info2.location = (xpos_ws, ypos_ws)
    n_obj_info2.parent = frame_s_bbe

    n_bb1 = node_group.nodes.new(type="GeometryNodeBoundBox")
    n_bb1.location = (xpos_ws+200, ypos_ws)
    n_bb1.parent = frame_s_bbe

    n_vmath_dist1 = node_group.nodes.new(type="ShaderNodeVectorMath")
    n_vmath_dist1.location = (xpos_ws+400, ypos_ws)
    n_vmath_dist1.operation = 'DISTANCE'
    n_vmath_dist1.parent = frame_s_bbe

    n_geo_prox1 = node_group.nodes.new(type="GeometryNodeProximity")
    n_geo_prox1.location = (xpos_ws+400, ypos)
    n_geo_prox1.target_element = 'POINTS'
    n_geo_prox1.parent = frame_s_ws

    n_map_range3 = node_group.nodes.new(type="ShaderNodeMapRange")
    n_map_range3.location = (xpos_ws+600, ypos_ws-0)
    n_map_range3.parent = frame_s_ws

    n_rgb_curve = node_group.nodes.new(type="ShaderNodeRGBCurve")
    n_rgb_curve.location = (xpos_ws+800, ypos_ws-0)
    mapping = n_rgb_curve.mapping
    print(mapping)
    curve = mapping.curves[-1]  #combined curve
    curve.points[0].location = (0.0,1.0)
    curve.points[1].location = (0.5,0.25)
    curve.points.new(1.0,0.15)
    n_rgb_curve.parent = frame_s_ws

    n_m_mult2 = node_group.nodes.new(type="ShaderNodeMath")
    n_m_mult2.location = (xpos_ws+1200, ypos_ws)
    n_m_mult2.operation = 'MULTIPLY'
    n_m_mult2.parent = frame_s_ws

    n_curve_circ1 = node_group.nodes.new(type="GeometryNodeCurvePrimitiveCircle")
    n_curve_circ1.location = (xpos_ws+1200, ypos-100)
    n_curve_circ1.inputs["Resolution"].default_value = 9
    n_curve_circ1.parent = frame_s_ws        

    n_curve2mesh = node_group.nodes.new(type="GeometryNodeCurveToMesh")
    n_curve2mesh.location = (xpos_ws+1400, ypos)
    n_curve2mesh.inputs["Fill Caps"].default_value = True
    n_curve2mesh.parent = frame_s_ws

    ##add links
    ###neurons
    node_group.links.new(n_group_input_1.outputs["Neuron Object"], n_bsnn_scale_rad1.inputs[0])
    node_group.links.new(n_neuron_surface_rand.outputs[0], n_m_mult1.inputs[1])
    node_group.links.new(n_bsnn_pos_glob1.outputs["Global Position"], n_noise_tex1.inputs[0])
    node_group.links.new(n_noise_tex1.outputs["Color"], n_m_mult1.inputs[0])
    node_group.links.new(n_m_mult1.outputs["Value"], n_bsnn_scale_rad1.inputs[1])
    node_group.links.new(n_bsnn_scale_rad1.outputs["Geometry"], n_join_geo.inputs[0])
    #node_group.links.new(n_join_geo.outputs["Geometry"], n_group_output_1.inputs[0])
    node_group.links.new(n_join_geo.outputs["Geometry"], n_mesh2grid.inputs["Mesh"])
    node_group.links.new(n_mesh2grid.outputs[0], n_voxelize.inputs["Grid"])
    node_group.links.new(n_voxelize.outputs["Grid"], n_grid2mesh.inputs["Grid"])
    node_group.links.new(n_grid2mesh.outputs["Mesh"], n_set_material.inputs["Geometry"])
    node_group.links.new(n_set_material.outputs[0], n_group_output_1.inputs["Neuron"])
    
    node_group.links.new(n_voxel_size.outputs[0], n_mesh2grid.inputs["Voxel Size"])
    node_group.links.new(n_threshold.outputs[0], n_grid2mesh.inputs["Threshold"])
    node_group.links.new(n_group_input_1.outputs["Neuron Material"], n_set_material.inputs["Material"])
    
    ###axons
    node_group.links.new(n_group_input_1.outputs["Axon Curve"], n_obj_info1.inputs["Object"])
    node_group.links.new(n_obj_info1.outputs["Geometry"], n_res_curve1.inputs["Curve"])
    node_group.links.new(n_res_curve1.outputs["Curve"], n_set_pos1.inputs["Geometry"])
    node_group.links.new(n_set_pos1.outputs["Geometry"], n_curve2mesh.inputs["Curve"])

    node_group.links.new(n_axon_res.outputs[0], n_res_curve1.inputs["Count"])
    node_group.links.new(n_curve2mesh.outputs["Mesh"], n_join_geo.inputs[0])
    node_group.links.new(n_noise_tex2.outputs["Color"], n_map_range2.inputs[0])
    node_group.links.new(n_map_range2.outputs["Result"], n_set_pos1.inputs["Offset"])

    node_group.links.new(n_group_input_1.outputs["Neuron Object"], n_geo_prox1.inputs["Geometry"])
    node_group.links.new(n_geo_prox1.outputs["Distance"], n_map_range3.inputs["Value"])
    node_group.links.new(n_map_range3.outputs["Result"], n_rgb_curve.inputs["Color"])
    node_group.links.new(n_rgb_curve.outputs["Color"], n_m_mult2.inputs["Value"])
    node_group.links.new(n_m_mult2.outputs["Value"], n_curve2mesh.inputs["Scale"])

    node_group.links.new(n_curve_circ1.outputs["Curve"], n_curve2mesh.inputs["Profile Curve"])

    node_group.links.new(n_group_input_1.outputs["Network Container"], n_obj_info2.inputs["Object"])
    node_group.links.new(n_obj_info2.outputs["Geometry"], n_bb1.inputs["Geometry"])
    node_group.links.new(n_bb1.outputs["Max"], n_vmath_dist1.inputs[0])
    node_group.links.new(n_bb1.outputs["Min"], n_vmath_dist1.inputs[1])
    node_group.links.new(n_vmath_dist1.outputs["Value"], n_map_range3.inputs["From Max"])
    node_group.links.new(n_axon_ref_width.outputs["Value"], n_m_mult2.inputs[1])
    
    return

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

    return



#%%registration
def register():
    network_container()
    neuron_axon()
    position_global()
    scale_radial()
    

def unregister():
    pass