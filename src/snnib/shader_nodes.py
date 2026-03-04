"""custom shader node node groups

- naming pattern: Snnib<Name>
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
def spiking_neuron():
    """creates base material for spiking neuron

    - this group is used to make created networks customizable in an intuitive manner
    """

    #group attributes
    mat_name = "SnnibSpikingNeuron"

    #creation
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()   #delete existing nodes

    #make nodes
    x0, y0 = 0, 0
    n_out = nodes.new(type="ShaderNodeOutputMaterial")
    n_out.location = (0,0)

    #main nodes
    n_frame_nb = nodes.new(type="NodeFrame")
    n_frame_nb.location = (0,0)
    n_frame_nb.label = "Neuron Body"

    n_tc = nodes.new(type="ShaderNodeTexCoord")
    n_tc.location = (x0, y0)
    n_tc.parent = n_frame_nb

    n_map1 = nodes.new(type="ShaderNodeMapping")
    n_map1.location = (x0+200, y0)
    n_map1.parent = n_frame_nb

    n_noise_tex1 = nodes.new(type="ShaderNodeTexNoise")
    n_noise_tex1.location = (x0+400, y0)
    n_noise_tex1.noise_dimensions = '4D'
    n_noise_tex1.parent = n_frame_nb

    n_cramp1 = nodes.new(type="ShaderNodeValToRGB")
    n_cramp1.location = (x0+600,y0)
    n_cramp1.color_ramp.elements[0].position = 0.35
    n_cramp1.color_ramp.elements[1].position = 0.85
    n_cramp1.parent = n_frame_nb

    n_cramp2 = nodes.new(type="ShaderNodeValToRGB")
    n_cramp2.location = (x0+1000,y0)
    n_cramp2.color_ramp.elements[0].position = 0.0
    n_cramp2.color_ramp.elements[1].position = 1.0
    n_cramp2.color_ramp.elements[0].color = (0.5, 0.3, 0.9, 1.0)
    n_cramp2.color_ramp.elements[1].color = (0.3, 0.1, 0.2, 1.0)
    n_cramp2.parent = n_frame_nb


    n_noise_tex2 = nodes.new(type="ShaderNodeTexNoise")
    n_noise_tex2.location = (x0+400, y0-400)
    n_noise_tex2.noise_dimensions = '4D'
    n_noise_tex2.inputs["Scale"].default_value = 0.6
    n_noise_tex2.parent = n_frame_nb

    n_map2 = nodes.new(type="ShaderNodeMapping")
    n_map2.location = (x0+200, y0-400)
    n_map2.parent = n_frame_nb

    n_cramp3 = nodes.new(type="ShaderNodeValToRGB")
    n_cramp3.location = (x0+600,y0-400)
    n_cramp3.parent = n_frame_nb
    n_cramp3.color_ramp.elements[0].position = 0.2
    n_cramp3.color_ramp.elements[1].position = 0.8

    n_bump = nodes.new(type="ShaderNodeBump")
    n_bump.location = (x0+1000,y0-400)
    n_bump.inputs["Strength"].default_value = 0.2
    n_bump.parent = n_frame_nb

    n_pr_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    n_pr_bsdf.location = (x0+1400,y0)
    n_pr_bsdf.inputs["Metallic"].default_value = 0.3
    n_pr_bsdf.inputs["Roughness"].default_value = 0.2
    n_pr_bsdf.inputs["IOR"].default_value = 5.0
    n_pr_bsdf.inputs[8].default_value = 0.7                 #Subsurface.Weight
    n_pr_bsdf.inputs[14].default_value = (0.7,0.5,1.0,1.0)  #Specular.Tint
    n_pr_bsdf.inputs[15].default_value = 0.45               #Specular.Anisotropic
    n_pr_bsdf.inputs[18].default_value = 0.10               #Transmission.Weight
    n_pr_bsdf.inputs[27].default_value = (1.0,0.5,0.7,1.0)  #Emission.Color
    n_pr_bsdf.inputs[28].default_value = 0.01               #Emission.Strength
    n_pr_bsdf.parent = n_frame_nb

    links = mat.node_tree.links
    links.new(n_tc.outputs["Object"], n_map1.inputs["Vector"])
    links.new(n_tc.outputs["Generated"], n_map2.inputs["Vector"])
    links.new(n_tc.outputs["Normal"], n_bump.inputs["Normal"])
    links.new(n_map1.outputs["Vector"], n_noise_tex1.inputs["Vector"])
    links.new(n_map2.outputs["Vector"], n_noise_tex2.inputs["Vector"])
    links.new(n_noise_tex1.outputs["Factor"], n_cramp1.inputs["Factor"])
    links.new(n_noise_tex2.outputs["Factor"], n_cramp3.inputs["Factor"])
    links.new(n_cramp1.outputs["Color"], n_cramp2.inputs["Factor"])
    links.new(n_cramp3.outputs["Color"], n_bump.inputs["Height"])
    links.new(n_cramp2.outputs["Color"], n_pr_bsdf.inputs["Base Color"])
    links.new(n_bump.outputs["Normal"], n_pr_bsdf.inputs["Normal"])

    #main nodes
    x0, y0 = (1000,400)

    n_tc = nodes.new(type="ShaderNodeTexCoord")
    n_tc.location = (x0, y0)

    n_map1 = nodes.new(type="ShaderNodeMapping")
    n_map1.location = (x0+200, y0)

    n_noise_tex1 = nodes.new(type="ShaderNodeTexNoise")
    n_noise_tex1.location = (x0+400, y0)
    n_noise_tex1.noise_dimensions = '4D'
    n_noise_tex1.inputs["Scale"].default_value = 2.0

    n_cramp1 = nodes.new(type="ShaderNodeValToRGB")
    n_cramp1.location = (x0+600,y0)
    n_cramp1.color_ramp.elements[0].position = 0.14
    n_cramp1.color_ramp.elements[1].position = 1.00
    n_cramp1.color_ramp.elements[0].color = (0.05,0.05,0.05,1.0)
    n_cramp1.color_ramp.elements[1].color = (0.75,0.75,0.75,1.0)

    n_transparent = nodes.new(type="ShaderNodeBsdfTransparent")
    n_transparent.location = (x0+800, y0-600)
    n_transparent.inputs["Color"].default_value = (0.45,0.45,0.45,1.00)

    n_mix_shader = nodes.new(type="ShaderNodeMixShader")
    n_mix_shader.location = (x0+1000, y0-400)

    links.new(n_tc.outputs["Object"], n_map1.inputs["Vector"])
    links.new(n_map1.outputs["Vector"], n_noise_tex1.inputs["Vector"])
    links.new(n_noise_tex1.outputs["Factor"], n_cramp1.inputs["Factor"])
    links.new(n_cramp1.outputs["Color"], n_mix_shader.inputs["Factor"])
    links.new(n_pr_bsdf.outputs["BSDF"], n_mix_shader.inputs[1])
    links.new(n_transparent.outputs["BSDF"], n_mix_shader.inputs[2])

    return

#%%registration
def register():
    #independent
    spiking_neuron()

def unregister():
    pass
