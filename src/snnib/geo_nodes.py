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
    length_max_in.default_value = 10.0
    
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
        name="Strength",
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
        name="Mesh",
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
    n_realize_instances.inputs["Depth"].default_value = 2
    n_realize_instances.location = (x0+600, y0-000)
        
    n_resample_curve = node_group.nodes.new(type="GeometryNodeResampleCurve")
    n_resample_curve.inputs["Mode"].default_value = 'Length'
    n_resample_curve.location = (x0+800, y0-0)
    
    n_snnib_neur_twist = node_group.nodes.new(type="GeometryNodeGroup")
    n_snnib_neur_twist.node_tree = bpy.data.node_groups["SnnibNeuriteTwist"]
    n_snnib_neur_twist.location = (x0+1000, y0)
    
    n_snnib_neur_bends = node_group.nodes.new(type="GeometryNodeGroup")
    n_snnib_neur_bends.node_tree = bpy.data.node_groups["SnnibNeuriteBends"]
    n_snnib_neur_bends.location = (x0+1200, y0)
    
    n_snnib_neur_to_mesh = node_group.nodes.new(type="GeometryNodeGroup")
    n_snnib_neur_to_mesh.node_tree = bpy.data.node_groups["SnnibNeuriteToMesh"]
    n_snnib_neur_to_mesh.location = (x0+1400, y0)

    #connect
    ##group inputs
    node_group.links.new(n_group_input_1.outputs["Host Mesh"], n_points_on_faces.inputs["Mesh"])
    node_group.links.new(n_group_input_1.outputs["Density"], n_points_on_faces.inputs["Density"])
    node_group.links.new(n_group_input_1.outputs["Seed"], n_points_on_faces.inputs["Seed"])
    node_group.links.new(n_group_input_1.outputs["Length.Min"], n_rand_float.inputs["Min"])
    node_group.links.new(n_group_input_1.outputs["Length.Max"], n_rand_float.inputs["Max"])
    node_group.links.new(n_group_input_1.outputs["Seed"], n_rand_float.inputs["Seed"])
    node_group.links.new(n_group_input_1.outputs["Resolution"], n_resample_curve.inputs["Length"])
    node_group.links.new(n_group_input_1.outputs["Twist"], n_snnib_neur_twist.inputs["Twist"])
    node_group.links.new(n_group_input_1.outputs["Strength"], n_snnib_neur_bends.inputs["Strength"])
    node_group.links.new(n_group_input_1.outputs["Scale"], n_snnib_neur_bends.inputs["Scale"])
    node_group.links.new(n_group_input_1.outputs["Diameter"], n_snnib_neur_to_mesh.inputs["Diameter"])
    node_group.links.new(n_group_input_1.outputs["Profile Resolution"], n_snnib_neur_to_mesh.inputs["Profile Resolution"])

    ##main nodes
    node_group.links.new(n_points_on_faces.outputs["Points"], n_instance_on_points.inputs["Points"])
    node_group.links.new(n_points_on_faces.outputs["Rotation"], n_instance_on_points.inputs["Rotation"])
    node_group.links.new(n_curve_line.outputs["Curve"], n_instance_on_points.inputs["Instance"])
    node_group.links.new(n_rand_float.outputs["Value"], n_instance_on_points.inputs["Scale"])
    node_group.links.new(n_instance_on_points.outputs["Instances"], n_realize_instances.inputs["Geometry"])
    node_group.links.new(n_realize_instances.outputs["Geometry"], n_resample_curve.inputs["Curve"])
    node_group.links.new(n_resample_curve.outputs["Curve"], n_snnib_neur_twist.inputs["Curve"])
    node_group.links.new(n_snnib_neur_twist.outputs["Curve"], n_snnib_neur_bends.inputs["Curve"])
    node_group.links.new(n_snnib_neur_bends.outputs["Curve"], n_snnib_neur_to_mesh.inputs["Curve"])
    node_group.links.new(n_snnib_neur_to_mesh.outputs["Mesh"], n_group_output_1.inputs["Mesh"])


    return

def neurite_to_mesh():
    """converts some input neurite (curve) to a mesh
    """
    
    #group attributes    
    group_name = "SnnibNeuriteToMesh"

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
    n_group_output_1.location = (x0+1400, y0+0)

    #generator nodes
    x0, y0 = 200, 0
    # utils.geo_nodes_utils.add_todo_node(node_group, (200,0))

    n_spline_param = node_group.nodes.new(type="GeometryNodeSplineParameter")
    n_spline_param.location = (x0, y0-200)

    n_m_sub = node_group.nodes.new(type="ShaderNodeMath")
    n_m_sub.operation = 'SUBTRACT'
    n_m_sub.inputs[0].default_value = 1.0
    n_m_sub.location = (x0+200, y0-200)
    
    n_rgb_curve = node_group.nodes.new(type="ShaderNodeRGBCurve")
    n_rgb_curve.location = (x0+400, y0-200)
    points = [[0.0,0.15],[0.02,0.85],[0.05,0.20],[1.0,1.0]]
    handle_types = ['AUTO','AUTO_CLAMPED','AUTO','AUTO']
    utils.geo_nodes_utils.set_node_curve(n_rgb_curve, 3, points, handle_types)
    n_rgb_curve.mapping.update()

    n_m_mult = node_group.nodes.new(type="ShaderNodeMath")
    n_m_mult.operation = 'MULTIPLY'
    n_m_mult.location = (x0+800, y0-200)

    n_curve_circ = node_group.nodes.new(type="GeometryNodeCurvePrimitiveCircle")
    n_curve_circ.location = (x0+800, y0-100)
    n_curve_circ.hide = True
    
    n_curve_to_mesh = node_group.nodes.new(type="GeometryNodeCurveToMesh")
    n_curve_to_mesh.inputs["Fill Caps"].default_value = True
    n_curve_to_mesh.location = (x0+1000, y0-0)
    
    node_group.links.new(n_group_input_1.outputs["Curve"], n_curve_to_mesh.inputs["Curve"])
    node_group.links.new(n_group_input_1.outputs["Diameter"], n_m_mult.inputs[0])
    node_group.links.new(n_group_input_1.outputs["Profile Resolution"], n_curve_circ.inputs["Resolution"])
    node_group.links.new(n_spline_param.outputs["Factor"], n_m_sub.inputs[1])
    node_group.links.new(n_m_sub.outputs["Value"], n_rgb_curve.inputs["Color"])
    node_group.links.new(n_rgb_curve.outputs["Color"], n_m_mult.inputs[1])
    node_group.links.new(n_m_mult.outputs["Value"], n_curve_to_mesh.inputs["Scale"])
    node_group.links.new(n_curve_circ.outputs["Curve"], n_curve_to_mesh.inputs["Profile Curve"])
    node_group.links.new(n_curve_to_mesh.outputs["Mesh"], n_group_output_1.inputs["Mesh"])


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

def neuron_neurites():
    """creates template geonodes node group for defining neurons and axons
    
    - this group is used to make created networks customizable in an intuitive manner 
    """
    
    #group attributes    
    group_name = "SnnibNeuronNeurites"

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

    #-------------------------------------------------------------
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
    n_spiketrain_offset.location = (x0+0, y0-400)
    n_spiketrain_offset.outputs[0].default_value = 0
    n_spiketrain_offset.parent = frame_cst

    n_spiketrain_stretch = node_group.nodes.new(type="ShaderNodeValue")
    n_spiketrain_stretch.label = "SpikeTrain.Stretch"
    n_spiketrain_stretch.location = (x0+0, y0-500)
    n_spiketrain_stretch.outputs[0].default_value = 0.2
    n_spiketrain_stretch.parent = frame_cst
    
    frame_ca = node_group.nodes.new(type="NodeFrame")
    frame_ca.label = "Neurites"
    frame_ca.location = (0,0)
    frame_ca.parent = frame_c     
    
    n_dendrite_diameter_scale = node_group.nodes.new(type="ShaderNodeValue")
    n_dendrite_diameter_scale.label = "Dendrite.Diameter.Scale"
    n_dendrite_diameter_scale.location = (x0+0, y0-700)
    n_dendrite_diameter_scale.outputs[0].default_value = 0.1
    n_dendrite_diameter_scale.parent = frame_ca

    n_dendrite_resolution = node_group.nodes.new(type="ShaderNodeValue")
    n_dendrite_resolution.label = "Dendrite.Resolution"
    n_dendrite_resolution.location = (x0+0, y0-800)
    n_dendrite_resolution.outputs[0].default_value = 0.1
    n_dendrite_resolution.parent = frame_ca
    
    n_axon_diameter_scale = node_group.nodes.new(type="ShaderNodeValue")
    n_axon_diameter_scale.label = "Axon.Diameter.Scale"
    n_axon_diameter_scale.location = (x0+0, y0-900)
    n_axon_diameter_scale.outputs[0].default_value = 0.3
    n_axon_diameter_scale.parent = frame_ca

    n_axon_resolution = node_group.nodes.new(type="ShaderNodeValue")
    n_axon_resolution.label = "Axon.Resolution"
    n_axon_resolution.location = (x0+0, y0-1000)
    n_axon_resolution.outputs[0].default_value = 0.1
    n_axon_resolution.parent = frame_ca

    #-------------------------------------------------------------
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
    n_m_div.operation = "DIVIDE"
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
    
    #-------------------------------------------------------------
    #dendrites
    x0, y0 = 300, -600
    frame_d = node_group.nodes.new(type="NodeFrame")
    frame_d.label = "Dendrites"
    frame_d.location = (0,0)

    n_snnib_neur_branches1 = node_group.nodes.new(type="GeometryNodeGroup")
    n_snnib_neur_branches1.node_tree = bpy.data.node_groups["SnnibNeuriteBranches"]
    n_snnib_neur_branches1.location = (x0, y0)
    n_snnib_neur_branches1.parent = frame_d

    n_join_geo1 = node_group.nodes.new(type="GeometryNodeJoinGeometry")
    n_join_geo1.location = (x0+400, y0)

    ##setting up repeat zone
    n_repeat_in = node_group.nodes.new(type="GeometryNodeRepeatInput")
    n_repeat_in.location = (x0+600, y0+0)    
    n_repeat_in.parent = frame_d
    n_repeat_out = node_group.nodes.new(type="GeometryNodeRepeatOutput")
    n_repeat_out.location = (x0+1400, y0+0)
    n_repeat_out.repeat_items.new("FLOAT", "Diameter")
    n_repeat_out.repeat_items.new("FLOAT", "Density")
    n_repeat_out.parent = frame_d
    n_repeat_in.pair_with_output(n_repeat_out)  #create pair
    n_repeat_in.inputs["Diameter"].default_value = 0.03
    n_repeat_in.inputs["Density"].default_value = 2.0

    n_snnib_neur_branches2 = node_group.nodes.new(type="GeometryNodeGroup")
    n_snnib_neur_branches2.node_tree = bpy.data.node_groups["SnnibNeuriteBranches"]
    n_snnib_neur_branches2.location = (x0+800, y0)
    n_snnib_neur_branches2.parent = frame_d

    n_join_geo2 = node_group.nodes.new(type="GeometryNodeJoinGeometry")
    n_join_geo2.location = (x0+1000, y0)

    ###updates
    n_m_mult = node_group.nodes.new(type="ShaderNodeMath")
    n_m_mult.operation = "MULTIPLY"
    n_m_mult.inputs[1].default_value = 0.5
    n_m_mult.location = (x0+800, y0-400)
    n_m_mult.parent = frame_d

    node_group.links.new(n_snnib_neur_branches1.outputs["Mesh"], n_join_geo1.inputs["Geometry"])
    node_group.links.new(n_join_geo1.outputs["Geometry"], n_repeat_in.inputs["Geometry"])
    node_group.links.new(n_repeat_in.outputs["Geometry"], n_snnib_neur_branches2.inputs["Host Mesh"])
    node_group.links.new(n_snnib_neur_branches2.outputs["Mesh"], n_join_geo2.inputs["Geometry"])
    node_group.links.new(n_join_geo2.outputs["Geometry"], n_repeat_out.inputs["Geometry"])


    node_group.links.new(n_group_input_1.outputs["Neuron Object"], n_snnib_neur_branches1.inputs["Host Mesh"])
    node_group.links.new(n_dendrite_resolution.outputs["Value"], n_snnib_neur_branches1.inputs["Resolution"])
    node_group.links.new(n_repeat_in.outputs["Geometry"], n_join_geo2.inputs["Geometry"])
    node_group.links.new(n_dendrite_diameter_scale.outputs["Value"], n_snnib_neur_branches1.inputs["Diameter"])
    node_group.links.new(n_repeat_in.outputs["Diameter"], n_m_mult.inputs[0])
    node_group.links.new(n_repeat_in.outputs["Diameter"], n_snnib_neur_branches2.inputs["Diameter"])
    node_group.links.new(n_repeat_in.outputs["Density"], n_snnib_neur_branches2.inputs["Density"])
    node_group.links.new(n_m_mult.outputs["Value"], n_repeat_out.inputs["Diameter"])
    
    #-------------------------------------------------------------
    #axon
    x0, y0 = 300, -1300
    frame_ax = node_group.nodes.new(type="NodeFrame")
    frame_ax.label = "Axon"
    frame_ax.location = (0,0)    
    
    n_obj_info = node_group.nodes.new(type="GeometryNodeObjectInfo")
    n_obj_info.location = (x0+0, y0-0)
    n_obj_info.transform_space = 'RELATIVE'
    n_obj_info.parent = frame_ax
    
    n_res_curve = node_group.nodes.new(type="GeometryNodeResampleCurve")
    n_res_curve.location = (x0+200, y0-0)
    n_res_curve.inputs["Mode"].default_value = 'Length'
    n_res_curve.parent = frame_ax
    
    n_snnib_neur_twist = node_group.nodes.new(type="GeometryNodeGroup")
    n_snnib_neur_twist.node_tree = bpy.data.node_groups["SnnibNeuriteTwist"]
    n_snnib_neur_twist.location = (x0+400, y0-0)
    n_snnib_neur_twist.parent = frame_ax
    
    n_snnib_neur_bends = node_group.nodes.new(type="GeometryNodeGroup")
    n_snnib_neur_bends.node_tree = bpy.data.node_groups["SnnibNeuriteBends"]
    n_snnib_neur_bends.location = (x0+600, y0-0)
    n_snnib_neur_bends.parent = frame_ax
    
    n_m_mult = node_group.nodes.new(type="ShaderNodeMath")
    n_m_mult.operation = 'MULTIPLY'
    n_m_mult.inputs[1].default_value = 3.0
    n_m_mult.location = (x0+600, y0-200)
    n_m_mult.parent = frame_ax
    
    n_snnib_neur_to_mesh = node_group.nodes.new(type="GeometryNodeGroup")
    n_snnib_neur_to_mesh.node_tree = bpy.data.node_groups["SnnibNeuriteToMesh"]
    n_snnib_neur_to_mesh.location = (x0+800, y0-0)
    n_snnib_neur_to_mesh.parent = frame_ax
    
    n_comb_xyz = node_group.nodes.new(type="ShaderNodeCombineXYZ")
    n_comb_xyz.location = (x0+800, y0-200)
    n_comb_xyz.inputs[0].default_value = 1.0
    n_comb_xyz.inputs[1].default_value = 1.0
    n_comb_xyz.inputs[2].default_value = 1.1
    n_comb_xyz.parent = frame_ax
    
    n_trans_geo = node_group.nodes.new(type="GeometryNodeTransform")
    n_trans_geo.location = (x0+1000, y0-0)
    n_trans_geo.parent = frame_ax

    node_group.links.new(n_group_input_1.outputs["Axon Curve"], n_obj_info.inputs["Object"])
    node_group.links.new(n_axon_resolution.outputs["Value"], n_res_curve.inputs["Length"])
    node_group.links.new(n_axon_diameter_scale.outputs["Value"], n_m_mult.inputs[0])
    node_group.links.new(n_obj_info.outputs["Geometry"], n_res_curve.inputs["Curve"])
    node_group.links.new(n_res_curve.outputs["Curve"], n_snnib_neur_twist.inputs["Curve"])
    node_group.links.new(n_snnib_neur_twist.outputs["Curve"], n_snnib_neur_bends.inputs["Curve"])
    node_group.links.new(n_snnib_neur_bends.outputs["Curve"], n_snnib_neur_to_mesh.inputs["Curve"])
    node_group.links.new(n_m_mult.outputs["Value"], n_snnib_neur_to_mesh.inputs["Diameter"])
    node_group.links.new(n_snnib_neur_to_mesh.outputs["Mesh"], n_trans_geo.inputs["Geometry"])
    node_group.links.new(n_comb_xyz.outputs["Vector"], n_trans_geo.inputs["Scale"])
    node_group.links.new(n_trans_geo.outputs["Geometry"], n_join_geo1.inputs["Geometry"])


    #-------------------------------------------------------------
    #combining
    x0, y0 = 2200, 0
    n_join_geo = node_group.nodes.new(type="GeometryNodeJoinGeometry")
    n_join_geo.location = (x0, y0)
    
    n_snnib_remesh = node_group.nodes.new(type="GeometryNodeGroup")
    n_snnib_remesh.node_tree = bpy.data.node_groups["SnnibRemesh"]
    n_snnib_remesh.location = (x0+200, y0-0)
    n_snnib_remesh.mute = True

    n_snnib_spiketrain = node_group.nodes.new(type="GeometryNodeGroup")
    n_snnib_spiketrain.node_tree = bpy.data.node_groups["SnnibSpiketrain"]
    n_snnib_spiketrain.location = (x0+400, y0+200)
    
    n_store_attr = node_group.nodes.new(type="GeometryNodeStoreNamedAttribute")
    n_store_attr.data_type = 'FLOAT_COLOR'
    n_store_attr.inputs["Name"].default_value = "Spiketrain.Texture"
    n_store_attr.location = (x0+600, y0)

    n_set_mat = node_group.nodes.new(type="GeometryNodeSetMaterial")
    n_set_mat.location = (x0+800, y0)
    n_set_mat.parent = utils.geo_nodes_utils.add_todo_node(node_group)

    n_shade_smooth = node_group.nodes.new(type="GeometryNodeSetShadeSmooth")
    n_shade_smooth.location = (x0+1000, y0)


    node_group.links.new(n_snnib_scale_rad.outputs["Geometry"], n_join_geo.inputs["Geometry"])
    node_group.links.new(n_repeat_out.outputs["Geometry"], n_join_geo.inputs["Geometry"])
    node_group.links.new(n_join_geo.outputs["Geometry"], n_snnib_remesh.inputs["Geometry"])
    node_group.links.new(n_snnib_remesh.outputs["Geometry"], n_snnib_spiketrain.inputs["Geometry"])
    node_group.links.new(n_group_input_1.outputs["Spiketrain"], n_snnib_spiketrain.inputs["Spiketrain"])
    node_group.links.new(n_spiketrain_offset.outputs["Value"], n_snnib_spiketrain.inputs["Offset"])
    node_group.links.new(n_spiketrain_stretch.outputs["Value"], n_snnib_spiketrain.inputs["Stretch"])
    node_group.links.new(n_n_frames.outputs["Value"], n_snnib_spiketrain.inputs["Number of Frames"])
    node_group.links.new(n_snnib_remesh.outputs["Geometry"], n_store_attr.inputs["Geometry"])
    node_group.links.new(n_snnib_spiketrain.outputs["Spiketrain"], n_store_attr.inputs["Value"])
    node_group.links.new(n_store_attr.outputs["Geometry"], n_set_mat.inputs["Geometry"])
    node_group.links.new(n_set_mat.outputs["Geometry"], n_shade_smooth.inputs["Mesh"])
    
    node_group.links.new(n_shade_smooth.outputs["Mesh"], n_group_output_1.inputs["Neuron"])
    

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

def remesh():
    """creates a geometry nodes node group similar to remesh modifier
    """

    #group attributes    
    group_name = "SnnibRemesh"

    #creation
    node_group = utils.geo_nodes_utils.create_node_group(group_name, dev=DEV)

    #define interface
    geo_in = node_group.interface.new_socket(
        name="Geometry",
        description="Geometry to be remeshed",
        in_out='INPUT',
        socket_type='NodeSocketGeometry'
    )
    voxel_size_in = node_group.interface.new_socket(
        name="Voxel Size",
        description="Size to use for the voxels",
        in_out='INPUT',
        socket_type='NodeSocketFloat'
    )
    voxel_size_in.default_value = 0.03
    threshold_in = node_group.interface.new_socket(
        name="Threshold",
        description="Threshold to use to convert voxelized geometry to mesh",
        in_out='INPUT',
        socket_type='NodeSocketFloat'
    )
    threshold_in.default_value = 0.03
    geo_out = node_group.interface.new_socket(
        name="Geometry",
        description="geometry after being scaled radially",
        in_out='OUTPUT',
        socket_type='NodeSocketGeometry'
    )

    #add nodes
    x0, y0 = 0, 0
    n_group_input_1 = node_group.nodes.new(type="NodeGroupInput")
    n_group_input_1.location = (x0, y0)
    n_group_output_1 = node_group.nodes.new(type="NodeGroupOutput")
    n_group_output_1.location = (800, 0)
    
    n_mesh_to_grid = node_group.nodes.new(type="GeometryNodeMeshToSDFGrid")
    n_mesh_to_grid.location = (x0+200, y0-0)
    
    n_voxelize = node_group.nodes.new(type="GeometryNodeGridVoxelize")
    n_voxelize.location = (x0+400, y0-0)
    
    n_grid_to_mesh = node_group.nodes.new(type="GeometryNodeGridToMesh")
    n_grid_to_mesh.location = (x0+600, y0-0)
    
    node_group.links.new(n_group_input_1.outputs["Geometry"], n_mesh_to_grid.inputs["Mesh"])
    node_group.links.new(n_group_input_1.outputs["Voxel Size"], n_mesh_to_grid.inputs["Voxel Size"])
    node_group.links.new(n_group_input_1.outputs["Threshold"], n_grid_to_mesh.inputs["Threshold"])
    node_group.links.new(n_mesh_to_grid.outputs["SDF Grid"], n_voxelize.inputs["Grid"])
    node_group.links.new(n_voxelize.outputs["Grid"], n_grid_to_mesh.inputs["Grid"])
    node_group.links.new(n_grid_to_mesh.outputs["Mesh"], n_group_output_1.inputs["Geometry"])

    return

def scale_radial():
    """creates a geometry nodes node group that scales input geometry radially
    """

    #group attributes    
    group_name = "SnnibScaleRadial"

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

def spiketrain():
    """creates a geometry nodes node group to generate colors for spiketrain

    - result stored as attribute
    """

    #group attributes    
    group_name = "SnnibSpiketrain"

    #creation
    node_group = utils.geo_nodes_utils.create_node_group(group_name, dev=DEV)

    #define interface
    geo_in = node_group.interface.new_socket(
        name="Geometry",
        description="Geometry to be remeshed",
        in_out='INPUT',
        socket_type='NodeSocketGeometry'
    )
    spiketrain_in = node_group.interface.new_socket(
        name="Spiketrain",
        description="1d image representing the spiketrain (pixels with values of 0 or 1)",
        in_out='INPUT',
        socket_type='NodeSocketImage'
    )
    offset_in = node_group.interface.new_socket(
        name="Offset",
        description="Offset of the spiketrain",
        in_out='INPUT',
        socket_type='NodeSocketInt'
    )
    stretch_in = node_group.interface.new_socket(
        name="Stretch",
        description="Stretch of the spiketrain",
        in_out='INPUT',
        socket_type='NodeSocketFloat'
    )
    nframes_in = node_group.interface.new_socket(
        name="Number of Frames",
        description="Number of frames in the entire animation",
        in_out='INPUT',
        socket_type='NodeSocketInt'
    )
    color_out = node_group.interface.new_socket(
        name="Spiketrain",
        description="Color representing the spiketrain",
        in_out='OUTPUT',
        socket_type='NodeSocketColor'
    )

    #add nodes
    x0, y0 = 0, 0
    n_group_input_1 = node_group.nodes.new(type="NodeGroupInput")
    n_group_input_1.location = (x0, y0)
    n_group_output_1 = node_group.nodes.new(type="NodeGroupOutput")
    n_group_output_1.location = (3000, 0)
    
    #-------------------------------------------------------------
    #r_norm
    x0, y0 = 200, 0
    frame_rn = node_group.nodes.new(type="NodeFrame")
    frame_rn.label = "r_norm \in [0,1]"
    frame_rn.location = (0,0)

    x0, y0 = 200, 0
    frame_r = node_group.nodes.new(type="NodeFrame")
    frame_r.label = "r \in \mathbb{R}"
    frame_r.location = (0,0)
    frame_r.parent = frame_rn

    n_pos = node_group.nodes.new(type="GeometryNodeInputPosition")
    n_pos.location = (x0, y0)
    n_pos.parent = frame_r
    
    n_obj_info = node_group.nodes.new(type="GeometryNodeObjectInfo")
    n_obj_info.location = (x0, y0-100)
    n_obj_info.parent = frame_r
    
    n_vm_dist1 = node_group.nodes.new(type="ShaderNodeVectorMath")
    n_vm_dist1.location = (x0+200, y0)
    n_vm_dist1.operation = "DISTANCE"
    n_vm_dist1.parent = frame_r

    node_group.links.new(n_pos.outputs["Position"], n_vm_dist1.inputs[0])
    node_group.links.new(n_obj_info.outputs["Location"], n_vm_dist1.inputs[1])

    x0, y0 = 200, -400
    frame_ro = node_group.nodes.new(type="NodeFrame")
    frame_ro.label = "Object radius \in \mathbb{R}"
    frame_ro.location = (0,0)
    frame_ro.parent = frame_rn

    n_bound_box = node_group.nodes.new(type="GeometryNodeBoundBox")
    n_bound_box.location = (x0, y0)
    n_bound_box.parent = frame_ro

    n_vm_dist2 = node_group.nodes.new(type="ShaderNodeVectorMath")
    n_vm_dist2.location = (x0+200, y0)
    n_vm_dist2.operation = "DISTANCE"
    n_vm_dist2.parent = frame_ro
    
    n_m_mult1 = node_group.nodes.new(type="ShaderNodeMath")
    n_m_mult1.location = (x0+400, y0)
    n_m_mult1.operation = "MULTIPLY"
    n_m_mult1.inputs[1].default_value = 0.5
    n_m_mult1.parent = frame_ro

    node_group.links.new(n_group_input_1.outputs["Geometry"], n_bound_box.inputs["Geometry"])
    node_group.links.new(n_bound_box.outputs["Min"], n_vm_dist2.inputs[0])
    node_group.links.new(n_bound_box.outputs["Max"], n_vm_dist2.inputs[1])
    node_group.links.new(n_vm_dist2.outputs["Value"], n_m_mult1.inputs[0])

    n_m_div1 = node_group.nodes.new(type="ShaderNodeMath")
    n_m_div1.location = (x0+600, y0+200)
    n_m_div1.operation = "DIVIDE"
    n_m_div1.parent = frame_rn

    node_group.links.new(n_vm_dist1.outputs["Value"], n_m_div1.inputs[0])
    node_group.links.new(n_m_mult1.outputs["Value"], n_m_div1.inputs[1])
    
    #-------------------------------------------------------------
    #time
    x0, y0 = 200, -700
    frame_t = node_group.nodes.new(type="NodeFrame")
    frame_t.label = "Time \in [-1,0]"
    frame_t.location = (0,0)

    n_scene_time = node_group.nodes.new(type="GeometryNodeInputSceneTime")
    n_scene_time.location = (x0, y0)
    n_scene_time.parent = frame_t
    
    n_m_div2 = node_group.nodes.new(type="ShaderNodeMath")
    n_m_div2.location = (x0+200, y0)
    n_m_div2.operation = "DIVIDE"
    n_m_div2.parent = frame_t
    
    n_m_mult2 = node_group.nodes.new(type="ShaderNodeMath")
    n_m_mult2.location = (x0+400, y0)
    n_m_mult2.operation = "MULTIPLY"
    n_m_mult2.inputs[1].default_value = -1.0
    n_m_mult2.parent = frame_t

    node_group.links.new(n_scene_time.outputs["Frame"], n_m_div2.inputs[0])
    node_group.links.new(n_group_input_1.outputs["Number of Frames"], n_m_div2.inputs[1])
    node_group.links.new(n_m_div2.outputs["Value"], n_m_mult2.inputs[0])

    #-------------------------------------------------------------
    #offset
    x0, y0 = 900, -400
    frame_os = node_group.nodes.new(type="NodeFrame")
    frame_os.label = "Offset"
    frame_os.location = (0,0)

    n_m_div3 = node_group.nodes.new(type="ShaderNodeMath")
    n_m_div3.location = (x0+200, y0)
    n_m_div3.operation = "DIVIDE"
    n_m_div3.parent = frame_os
    
    n_m_sub = node_group.nodes.new(type="ShaderNodeMath")
    n_m_sub.location = (x0+400, y0)
    n_m_sub.operation = "SUBTRACT"
    n_m_sub.parent = frame_os

    node_group.links.new(n_group_input_1.outputs["Offset"], n_m_div3.inputs[0])
    node_group.links.new(n_group_input_1.outputs["Number of Frames"], n_m_div3.inputs[1])
    node_group.links.new(n_m_div1.outputs["Value"], n_m_sub.inputs[0])
    node_group.links.new(n_m_div3.outputs["Value"], n_m_sub.inputs[1])

    #-------------------------------------------------------------
    #stretch
    x0, y0 = 1600, -400
    frame_st = node_group.nodes.new(type="NodeFrame")
    frame_st.label = "Stretch"
    frame_st.location = (0,0)

    n_m_mult3 = node_group.nodes.new(type="ShaderNodeMath")
    n_m_mult3.location = (x0, y0)
    n_m_mult3.operation = "MULTIPLY"
    n_m_mult3.parent = frame_st

    node_group.links.new(n_m_sub.outputs["Value"], n_m_mult3.inputs[0])
    node_group.links.new(n_group_input_1.outputs["Stretch"], n_m_mult3.inputs[1])

    #-------------------------------------------------------------
    #index
    x0, y0 = 2000, -400
    frame_id = node_group.nodes.new(type="NodeFrame")
    frame_id.label = "Index \in [0,1]"
    frame_id.location = (0,0)

    n_m_add = node_group.nodes.new(type="ShaderNodeMath")
    n_m_add.location = (x0, y0)
    n_m_add.operation = "ADD"
    n_m_add.parent = frame_id

    n_m_sub = node_group.nodes.new(type="ShaderNodeMath")
    n_m_sub.location = (x0+200, y0)
    n_m_sub.operation = "SUBTRACT"
    n_m_sub.inputs[0].default_value = 1.0
    n_m_sub.parent = frame_id

    n_comb_xyz = node_group.nodes.new(type="ShaderNodeCombineXYZ")
    n_comb_xyz.location = (x0+400, y0)
    n_comb_xyz.inputs["Y"].default_value = 1.0
    n_comb_xyz.inputs["Z"].default_value = 1.0
    n_comb_xyz.parent = frame_id
    
    node_group.links.new(n_m_mult3.outputs["Value"], n_m_add.inputs[0])
    node_group.links.new(n_m_mult2.outputs["Value"], n_m_add.inputs[1])
    node_group.links.new(n_m_add.outputs["Value"], n_m_sub.inputs[1])
    node_group.links.new(n_m_sub.outputs["Value"], n_comb_xyz.inputs["X"])

    n_img_tex = node_group.nodes.new(type="GeometryNodeImageTexture")
    n_img_tex.location = (x0+600, y0)

    node_group.links.new(n_group_input_1.outputs["Spiketrain"], n_img_tex.inputs["Image"])
    node_group.links.new(n_comb_xyz.outputs["Vector"], n_img_tex.inputs["Vector"])
    node_group.links.new(n_img_tex.outputs["Color"], n_group_output_1.inputs["Spiketrain"])

    return

#%%registration
def register():
    #independent
    neurite_to_mesh()
    neurite_bends()
    neurite_twist()
    position_global()
    remesh()
    scale_radial()
    spiketrain() 

    #dependent
    neurite_branches()
    # network_container()
    neuron_neurites()
    

def unregister():
    pass