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

import importlib
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from . import (DEV, utils)

importlib.reload(utils)
  
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

def neurite_bends():
    """applies twist to some curve
    """
    
    #group attributes    
    group_name = "SnnibNeuriteBends"

    #creation
    node_group = utils.geo_nodes_utils.create_node_group(group_name, dev=DEV)

    #define interface
    host_in = node_group.interface.new_socket(
        name="Curve",
        description="Curve to apply bends to",
        in_out='INPUT',
        socket_type='NodeSocketGeometry',
    )
    
    twist_in = node_group.interface.new_socket(
        name="Strength",
        description="Strength of the applied bends",
        in_out='INPUT',
        socket_type='NodeSocketFloat',
    )
    twist_in.default_value = 1.0
    
    twist_in = node_group.interface.new_socket(
        name="Scale",
        description="Scale of the applied bends",
        in_out='INPUT',
        socket_type='NodeSocketFloat',
    )
    twist_in.default_value = 1.0
    
    curve_out = node_group.interface.new_socket(
        name="Curve",
        description="Input `Curve` with bends applied",
        in_out='OUTPUT',
        socket_type='NodeSocketGeometry'
    )
    #add i/o nodes
    x0, y0 = 0, 0
    n_group_input_1 = node_group.nodes.new(type="NodeGroupInput")
    n_group_input_1.location = (x0+0, y0+0)
    n_group_output_1 = node_group.nodes.new(type="NodeGroupOutput")
    n_group_output_1.location = (x0+2000, y0+0)

    #main nodes
    x0, y0 = 200, 0

    n_noise_tex = node_group.nodes.new(type="ShaderNodeTexNoise")
    n_noise_tex.location = (x0+0, y0-400)
    n_noise_tex.noise_dimensions = '4D'
    n_noise_tex.inputs["Roughness"].default_value = 0.2
    n_noise_tex.inputs["Distortion"].default_value = 1.0
    
    n_sep_xyz = node_group.nodes.new(type="ShaderNodeSeparateXYZ")
    n_sep_xyz.location = (x0+200, y0-400)

    n_m_mult = node_group.nodes.new(type="ShaderNodeMath")
    n_m_mult.operation = 'MULTIPLY'
    n_m_mult.inputs[1].default_value = -1.0
    n_m_mult.location = (x0+200, y0-200)
    n_m_mult.hide = True

    n_m_maprange1 = node_group.nodes.new(type="ShaderNodeMapRange")
    n_m_maprange1.location = (x0+400, y0-400)
    n_m_maprange1.hide = True

    n_m_maprange2 = node_group.nodes.new(type="ShaderNodeMapRange")
    n_m_maprange2.location = (x0+400, y0-500)
    n_m_maprange2.hide = True

    n_comb_xyz = node_group.nodes.new(type="ShaderNodeCombineXYZ")
    n_comb_xyz.inputs["Z"].default_value = 0.0
    n_comb_xyz.location = (x0+600, y0-400)

    n_normal = node_group.nodes.new(type="GeometryNodeInputNormal")
    n_normal.location = (x0+600, y0-600)

    n_vm_project = node_group.nodes.new(type="ShaderNodeVectorMath")
    n_vm_project.operation = 'PROJECT'
    n_vm_project.location = (x0+800, y0-400)

    n_spline_param = node_group.nodes.new(type="GeometryNodeSplineParameter")
    n_spline_param.location = (x0+800, y0-200)

    n_rgb_curve = node_group.nodes.new(type="ShaderNodeRGBCurve")
    n_rgb_curve.location = (x0+1000, y0-0)
    points = [[0.0,0.0],[0.07,0.0],[0.24,0.90],[1.0,1.0]]
    handle_types = ['AUTO_CLAMPED','AUTO_CLAMPED','AUTO_CLAMPED','AUTO']
    utils.geo_nodes_utils.set_node_curve(n_rgb_curve, 3, points, handle_types)
    n_rgb_curve.mapping.update()
    
    n_vm_mult = node_group.nodes.new(type="ShaderNodeVectorMath")
    n_vm_mult.operation = 'MULTIPLY'
    n_vm_mult.location = (x0+1400, y0-200)
    
    n_set_pos = node_group.nodes.new(type="GeometryNodeSetPosition")
    n_set_pos.location = (x0+1600, y0-100)

    node_group.links.new(n_group_input_1.outputs["Curve"], n_set_pos.inputs["Geometry"])
    node_group.links.new(n_group_input_1.outputs["Strength"], n_m_mult.inputs[0])
    node_group.links.new(n_group_input_1.outputs["Strength"], n_m_maprange1.inputs["To Max"])
    node_group.links.new(n_group_input_1.outputs["Strength"], n_m_maprange2.inputs["To Max"])
    node_group.links.new(n_m_mult.outputs["Value"], n_m_maprange1.inputs["To Min"])
    node_group.links.new(n_m_mult.outputs["Value"], n_m_maprange2.inputs["To Min"])
    node_group.links.new(n_group_input_1.outputs["Scale"], n_noise_tex.inputs["Scale"])
    node_group.links.new(n_noise_tex.outputs["Color"], n_sep_xyz.inputs["Vector"])
    node_group.links.new(n_sep_xyz.outputs["X"], n_m_maprange1.inputs["Value"])
    node_group.links.new(n_sep_xyz.outputs["Y"], n_m_maprange2.inputs["Value"])
    node_group.links.new(n_m_maprange1.outputs["Result"], n_comb_xyz.inputs["X"])
    node_group.links.new(n_m_maprange2.outputs["Result"], n_comb_xyz.inputs["Y"])
    node_group.links.new(n_comb_xyz.outputs["Vector"], n_vm_project.inputs[0])
    node_group.links.new(n_normal.outputs["Normal"], n_vm_project.inputs[1])
    node_group.links.new(n_spline_param.outputs["Factor"], n_rgb_curve.inputs["Color"])
    node_group.links.new(n_rgb_curve.outputs["Color"], n_vm_mult.inputs[0])
    node_group.links.new(n_vm_project.outputs["Vector"], n_vm_mult.inputs[1])
    node_group.links.new(n_vm_mult.outputs["Vector"], n_set_pos.inputs["Offset"])
    node_group.links.new(n_set_pos.outputs["Geometry"], n_group_output_1.inputs["Curve"])

    return

def neurite_branches():
    """creates a set of branches in random directions originating at `Host Mesh`

    - used to procedurally generate non-connections
    """
    
    #group attributes    
    group_name = "SnnibNeuriteBranches"

    #creation
    node_group = utils.geo_nodes_utils.create_node_group(group_name, dev=DEV)

    #define interface
    host_in = node_group.interface.new_socket(
        name="Host Mesh",
        description="Host mesh serving as origin to neurites",
        in_out='INPUT',
        socket_type='NodeSocketGeometry',
    )

    density_in = node_group.interface.new_socket(
        name="Density",
        description="Density of the randomly generated neurites on the `Host Mesh`",
        in_out='INPUT',
        socket_type='NodeSocketFloat',
    )
    density_in.min_value = 0.0
    density_in.default_value = 0.3
    
    length_min_in = node_group.interface.new_socket(
        name="Length.Min",
        description="Minimum length of any neurite",
        in_out='INPUT',
        socket_type='NodeSocketFloat',
    )
    length_min_in.min_value = 0.0
    length_min_in.default_value = 3.0
    
    length_max_in = node_group.interface.new_socket(
        name="Length.Max",
        description="Maximum length of any neurite",
        in_out='INPUT',
        socket_type='NodeSocketFloat',
    )
    length_max_in.min_value = 0.0
    length_max_in.default_value = 3.0
    
    seed_in = node_group.interface.new_socket(
        name="Seed",
        description="Random seed for the distribution",
        in_out='INPUT',
        socket_type='NodeSocketInt',
    )
    seed_in.default_value = 0
    
    resolution_in = node_group.interface.new_socket(
        name="Resolution",
        description="Resolution of the generated neurite in meters",
        in_out='INPUT',
        socket_type='NodeSocketFloat',
    )
    resolution_in.default_value = 0.1
    
    twist_in = node_group.interface.new_socket(
        name="Twist",
        description="Amount twist of the generated neurite",
        in_out='INPUT',
        socket_type='NodeSocketFloat',
    )
    twist_in.default_value = 14
    
    bend_strength_in = node_group.interface.new_socket(
        name="Bend",
        description="Strength of the random bends of the generated neurite",
        in_out='INPUT',
        socket_type='NodeSocketFloat',
    )
    bend_strength_in.default_value = 1.0
    
    bend_scale_in = node_group.interface.new_socket(
        name="Scale",
        description="Scale of the random bends of the generated neurite",
        in_out='INPUT',
        socket_type='NodeSocketFloat',
    )
    bend_scale_in.default_value = 1.0
    
    diameter_in = node_group.interface.new_socket(
        name="Diameter",
        description="Scaling factor of neurite diameter",
        in_out='INPUT',
        socket_type='NodeSocketFloat',
    )
    diameter_in.default_value = 0.1
    
    resolution_profile_in = node_group.interface.new_socket(
        name="Profile Resolution",
        description="Resolution of the profile curve used to convert axons to mesh",
        in_out='INPUT',
        socket_type='NodeSocketInt',
    )
    resolution_profile_in.default_value = 16
    
    neuron_out = node_group.interface.new_socket(
        name="Host Mesh",
        description="`Host Mesh` including neurite branches",
        in_out='OUTPUT',
        socket_type='NodeSocketGeometry'
    )    

    #add i/o nodes
    x0, y0 = 0, 0
    n_group_input_1 = node_group.nodes.new(type="NodeGroupInput")
    n_group_input_1.location = (x0+0, y0+0)
    n_group_output_1 = node_group.nodes.new(type="NodeGroupOutput")
    n_group_output_1.location = (x0+1800, y0+0)

    #generator nodes
    x0, y0 = 200, 0
    n_points_on_faces = node_group.nodes.new(type="GeometryNodeDistributePointsOnFaces")
    n_points_on_faces.location = (x0+000, y0+100)
    
    n_rand_float = node_group.nodes.new(type="FunctionNodeRandomValue")
    n_rand_float.data_type = 'FLOAT'
    n_rand_float.location = (x0+200, y0-100)
    
    n_curve_line = node_group.nodes.new(type="GeometryNodeCurvePrimitiveLine")
    n_curve_line.location = (x0+200, y0-0)
    n_curve_line.hide = True
    
    n_instance_on_points = node_group.nodes.new(type="GeometryNodeInstanceOnPoints")
    n_instance_on_points.location = (x0+400, y0-0)
    
    n_realize_instances = node_group.nodes.new(type="GeometryNodeRealizeInstances")
    n_realize_instances.location = (x0+600, y0-000)
        
    n_resample_curve = node_group.nodes.new(type="GeometryNodeResampleCurve")
    n_resample_curve.location = (x0+800, y0-0)
    
    n_snnib_neur_twist = node_group.nodes.new(type="GeometryNodeGroup")
    n_snnib_neur_twist.node_tree = bpy.data.node_groups["SnnibNeuriteTwist"]
    n_snnib_neur_twist.location = (x0+1000, y0)
    
    n_snnib_neur_bends = node_group.nodes.new(type="GeometryNodeGroup")
    n_snnib_neur_bends.node_tree = bpy.data.node_groups["SnnibNeuriteBends"]
    n_snnib_neur_bends.location = (x0+1200, y0)
    
    n_snnib_neur_curve_shape = node_group.nodes.new(type="GeometryNodeGroup")
    n_snnib_neur_curve_shape.node_tree = bpy.data.node_groups["SnnibNeuriteCurveShape"]
    n_snnib_neur_curve_shape.location = (x0+1400, y0)

    return

def neurite_curve_shape():
    """creates a set of branches in random directions originating at `Host Mesh`

    - used to procedurally generate non-connections
    """
    
    #group attributes    
    group_name = "SnnibNeuriteCurveShape"

    #creation
    node_group = utils.geo_nodes_utils.create_node_group(group_name, dev=DEV)

    #define interface
    curve_in = node_group.interface.new_socket(
        name="Curve",
        description="Curve representing the neuron",
        in_out='INPUT',
        socket_type='NodeSocketGeometry',
    )

    diameter_in = node_group.interface.new_socket(
        name="Diameter",
        description="Scaling of the diameter that the input `curve` shall have",
        in_out='INPUT',
        socket_type='NodeSocketFloat',
    )
    diameter_in.default_value = 0.1
    
    resolution_profile_in = node_group.interface.new_socket(
        name="Profile Resolution",
        description="Resolution of the profile curve used to generate mesh",
        in_out='INPUT',
        socket_type='NodeSocketInt',
    )
    resolution_profile_in.default_value = 16
    
    mesh_out = node_group.interface.new_socket(
        name="Mesh",
        description="`Curve` converted to a mesh",
        in_out='OUTPUT',
        socket_type='NodeSocketGeometry'
    )    

    #add i/o nodes
    x0, y0 = 0, 0
    n_group_input_1 = node_group.nodes.new(type="NodeGroupInput")
    n_group_input_1.location = (x0+0, y0+0)
    n_group_output_1 = node_group.nodes.new(type="NodeGroupOutput")
    n_group_output_1.location = (x0+800, y0+0)

    #generator nodes
    x0, y0 = 200, 0
    utils.geo_nodes_utils.add_todo_node(node_group, (200,0))


    return

def neurite_twist():
    """applies twist to some curve
    """
    
    #group attributes    
    group_name = "SnnibNeuriteTwist"

    #creation
    node_group = utils.geo_nodes_utils.create_node_group(group_name, dev=DEV)

    #define interface
    host_in = node_group.interface.new_socket(
        name="Curve",
        description="Curve to be twisted",
        in_out='INPUT',
        socket_type='NodeSocketGeometry',
    )
    
    twist_in = node_group.interface.new_socket(
        name="Twist",
        description="Amount twist of the generated neurite",
        in_out='INPUT',
        socket_type='NodeSocketFloat',
    )
    twist_in.default_value = 14
    
    curve_out = node_group.interface.new_socket(
        name="Curve",
        description="Input `Curve` with twist applied",
        in_out='OUTPUT',
        socket_type='NodeSocketGeometry'
    )    
    #add i/o nodes
    x0, y0 = 0, 0
    n_group_input_1 = node_group.nodes.new(type="NodeGroupInput")
    n_group_input_1.location = (x0+0, y0+0)
    n_group_output_1 = node_group.nodes.new(type="NodeGroupOutput")
    n_group_output_1.location = (x0+1200, y0+0)

    #main nodes
    x0, y0 = 200, 0
    n_spline_param = node_group.nodes.new(type="GeometryNodeSplineParameter")
    n_spline_param.location = (x0+0, y0-200)
    
    n_rgb_curve = node_group.nodes.new(type="ShaderNodeRGBCurve")
    n_rgb_curve.location = (x0+200, y0-200)
    points = [[0.0,0.45],[0.33,0.75],[1.0,1.0]]
    utils.geo_nodes_utils.set_node_curve(n_rgb_curve, 3, points)
    n_rgb_curve.mapping.update()
    
    n_m_mult = node_group.nodes.new(type="ShaderNodeMath")
    n_m_mult.operation = 'MULTIPLY'
    n_m_mult.location = (x0+600, y0-100)
    
    n_curve_tilt = node_group.nodes.new(type="GeometryNodeSetCurveTilt")
    n_curve_tilt.location = (x0+800, y0-0)

    node_group.links.new(n_group_input_1.outputs["Curve"], n_curve_tilt.inputs["Curve"])
    node_group.links.new(n_group_input_1.outputs["Twist"], n_m_mult.inputs[0])
    node_group.links.new(n_spline_param.outputs["Factor"], n_rgb_curve.inputs["Color"])
    node_group.links.new(n_rgb_curve.outputs["Color"], n_m_mult.inputs[1])
    node_group.links.new(n_m_mult.outputs["Value"], n_curve_tilt.inputs["Tilt"])
    node_group.links.new(n_curve_tilt.outputs["Curve"], n_group_output_1.inputs["Curve"])

    return

def neuron_axon():
    """creates template geonodes node group for defining neurons and axons
    
    - this group is used to make created networks customizable in an intuitive manner 
    """
    
    #group attributes    
    group_name = "SnnibNeuronAxon"

    #creation
    node_group = utils.geo_nodes_utils.create_node_group(group_name, dev=DEV)

    #define interface
    neuron_in = node_group.interface.new_socket(
        name="Neuron Object",
        description="Neuron",
        in_out='INPUT',
        socket_type='NodeSocketGeometry'
    )
    spiketrain_in = node_group.interface.new_socket(
        name="Spiketrain",
        description="1D texture map representing the spiketrain",
        in_out='INPUT',
        socket_type='NodeSocketImage'
    )
    axon_in = node_group.interface.new_socket(
        name="Axon Curve",
        description="Curve representing the neurons axon",
        in_out='INPUT',
        socket_type='NodeSocketObject'
    )
    
    neuron_out = node_group.interface.new_socket(
        name="Neuron",
        description="Neuron inluding axon",
        in_out='OUTPUT',
        socket_type='NodeSocketGeometry'
    )

    #add i/o nodes
    x0, y0 = 0, 0
    n_group_input_1 = node_group.nodes.new(type="NodeGroupInput")
    n_group_input_1.location = (x0+0, y0+0)
    n_group_output_1 = node_group.nodes.new(type="NodeGroupOutput")
    n_group_output_1.location = (x0+4200, y0+0)

    
    #control values
    x0, y0 = 0, -200
    frame_c = node_group.nodes.new(type="NodeFrame")
    frame_c.label = "Controls"
    frame_c.location = (0,0)

    n_n_frames = node_group.nodes.new(type="ShaderNodeValue")
    n_n_frames.label = "Number of Frames"
    n_n_frames.location = (x0+0, y0)
    n_n_frames.outputs[0].default_value = 120
    n_n_frames.parent = frame_c

    frame_cn = node_group.nodes.new(type="NodeFrame")
    frame_cn.label = "Neuron"
    frame_cn.location = (0,0)
    frame_cn.parent = frame_c
    
    n_neuron_pulsation_slowdown = node_group.nodes.new(type="ShaderNodeValue")
    n_neuron_pulsation_slowdown.label = "Neuron.Pulsation.Slowdown"
    n_neuron_pulsation_slowdown.location = (x0+0, y0-100)
    n_neuron_pulsation_slowdown.outputs[0].default_value = 75
    n_neuron_pulsation_slowdown.parent = frame_cn
    
    n_neuron_pulsation_scale = node_group.nodes.new(type="ShaderNodeValue")
    n_neuron_pulsation_scale.label = "Neuron.Pulsation.Scale"
    n_neuron_pulsation_scale.location = (x0+0, y0-200)
    n_neuron_pulsation_scale.outputs[0].default_value = 0.5
    n_neuron_pulsation_scale.parent = frame_cn
    
    frame_cst = node_group.nodes.new(type="NodeFrame")
    frame_cst.label = "Spike Train"
    frame_cst.location = (0,0)
    frame_cst.parent = frame_c 
    
    n_spiketrain_offset = node_group.nodes.new(type="ShaderNodeValue")
    n_spiketrain_offset.label = "SpikeTrain.Offset"
    n_spiketrain_offset.location = (x0+0, y0-300)
    n_spiketrain_offset.outputs[0].default_value = 0
    n_spiketrain_offset.parent = frame_cst

    n_spiketrain_stretch = node_group.nodes.new(type="ShaderNodeValue")
    n_spiketrain_stretch.label = "SpikeTrain.Stretch"
    n_spiketrain_stretch.location = (x0+0, y0-400)
    n_spiketrain_stretch.outputs[0].default_value = 0.2
    n_spiketrain_stretch.parent = frame_cst
    
    frame_ca = node_group.nodes.new(type="NodeFrame")
    frame_ca.label = "Axon"
    frame_ca.location = (0,0)
    frame_ca.parent = frame_c     

    n_axon_diameter_scale = node_group.nodes.new(type="ShaderNodeValue")
    n_axon_diameter_scale.label = "Axon.Diameter.Scale"
    n_axon_diameter_scale.location = (x0+0, y0-500)
    n_axon_diameter_scale.outputs[0].default_value = 0.1
    n_axon_diameter_scale.parent = frame_ca

    n_axon_resolution = node_group.nodes.new(type="ShaderNodeValue")
    n_axon_resolution.label = "Axon.Resolution"
    n_axon_resolution.location = (x0+0, y0-600)
    n_axon_resolution.outputs[0].default_value = 0.1
    n_axon_resolution.parent = frame_ca
    
    #neuron body
    x0 = 300
    y0 = -0
    frame_nb = node_group.nodes.new(type="NodeFrame")
    frame_nb.label = "Neuron Body"
    frame_nb.location = (0,0)

    n_scene_time = node_group.nodes.new(type="GeometryNodeInputSceneTime")
    n_scene_time.location = (x0+000, y0-100)
    n_scene_time.parent = frame_nb

    n_snnib_pos_glob = node_group.nodes.new(type="GeometryNodeGroup")
    n_snnib_pos_glob.node_tree = bpy.data.node_groups["SnnibPositionGlobal"]
    n_snnib_pos_glob.location = (x0+200, y0)
    n_snnib_pos_glob.parent = frame_nb

    n_m_div = node_group.nodes.new(type="ShaderNodeMath")
    n_m_div.operation = "MULTIPLY"
    n_m_div.location = (x0+200, y0-100)
    n_m_div.parent = frame_nb

    n_noise_tex = node_group.nodes.new(type="ShaderNodeTexNoise")
    n_noise_tex.location = (x0+400, y0-0)
    n_noise_tex.noise_dimensions = '4D'
    n_noise_tex.inputs["Scale"].default_value = 2.0
    n_noise_tex.parent = frame_nb
    
    n_m_mult = node_group.nodes.new(type="ShaderNodeMath")
    n_m_mult.operation = "MULTIPLY"
    n_m_mult.location = (x0+600, y0-0)
    n_m_mult.parent = frame_nb        

    n_snnib_scale_rad = node_group.nodes.new(type="GeometryNodeGroup")
    n_snnib_scale_rad.node_tree = bpy.data.node_groups["SnnibScaleRadial"]
    n_snnib_scale_rad.location = (x0+800, y0-0)
    n_snnib_scale_rad.parent = frame_nb

    node_group.links.new(n_group_input_1.outputs["Neuron Object"], n_snnib_scale_rad.inputs["Geometry"])
    node_group.links.new(n_scene_time.outputs["Frame"], n_m_div.inputs[0])
    node_group.links.new(n_neuron_pulsation_slowdown.outputs["Value"], n_m_div.inputs[1])
    node_group.links.new(n_m_div.outputs["Value"], n_noise_tex.inputs["W"])
    node_group.links.new(n_snnib_pos_glob.outputs["Global Position"], n_noise_tex.inputs["Vector"])
    node_group.links.new(n_noise_tex.outputs["Factor"], n_m_mult.inputs[0])
    node_group.links.new(n_m_mult.outputs["Value"], n_snnib_scale_rad.inputs["Scale"])
    
    #dendrites
    x0, y0 = 300, -600
    frame_d = node_group.nodes.new(type="NodeFrame")
    frame_d.label = "Dendrites"
    frame_d.location = (0,0)

    n_snnib_pos_glob = node_group.nodes.new(type="GeometryNodeGroup")
    n_snnib_pos_glob.node_tree = bpy.data.node_groups["SnnibNeuriteBranches"]
    n_snnib_pos_glob.location = (x0, y0)
    n_snnib_pos_glob.parent = frame_d


    return

def neuron_axon_old():
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

    n_snnib_pos_glob1 = node_group.nodes.new(type="GeometryNodeGroup")
    n_snnib_pos_glob1.node_tree = bpy.data.node_groups["SnnibPositionGlobal"]
    n_snnib_pos_glob1.location = (xpos_n, 000)
    n_snnib_pos_glob1.parent = frame_n

    n_noise_tex1 = node_group.nodes.new(type="ShaderNodeTexNoise")
    n_noise_tex1.location = (xpos_n + 200, 000)
    n_noise_tex1.noise_dimensions = '4D'
    n_noise_tex1.parent = frame_n

    n_m_mult1 = node_group.nodes.new(type="ShaderNodeMath")
    n_m_mult1.operation = "MULTIPLY"
    n_m_mult1.location = (xpos_n+400, 000)
    n_m_mult1.parent = frame_n        

    n_snnib_scale_rad1 = node_group.nodes.new(type="GeometryNodeGroup")
    n_snnib_scale_rad1.node_tree = bpy.data.node_groups["SnnibScaleRadial"]
    n_snnib_scale_rad1.location = (xpos_n+600, 000)
    n_snnib_scale_rad1.parent = frame_n        

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
    node_group.links.new(n_group_input_1.outputs["Neuron Object"], n_snnib_scale_rad1.inputs[0])
    node_group.links.new(n_neuron_surface_rand.outputs[0], n_m_mult1.inputs[1])
    node_group.links.new(n_snnib_pos_glob1.outputs["Global Position"], n_noise_tex1.inputs[0])
    node_group.links.new(n_noise_tex1.outputs["Color"], n_m_mult1.inputs[0])
    node_group.links.new(n_m_mult1.outputs["Value"], n_snnib_scale_rad1.inputs[1])
    node_group.links.new(n_snnib_scale_rad1.outputs["Geometry"], n_join_geo.inputs[0])
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

    #creation
    node_group = utils.geo_nodes_utils.create_node_group(group_name, dev=DEV)

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

    #creation
    node_group = utils.geo_nodes_utils.create_node_group(group_name, dev=DEV)

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
    #independent
    neurite_curve_shape()
    neurite_bends()
    neurite_twist()
    position_global()
    scale_radial()

    #dependent
    neurite_branches()
    # network_container()
    neuron_axon()
    

def unregister():
    pass