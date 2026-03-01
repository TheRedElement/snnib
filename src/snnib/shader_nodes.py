"""custom geo node node groups

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

    n_tc = nodes.new(type="ShaderNodeTexCoord")
    n_tc.location = (x0, y0)
    
    n_map = nodes.new(type="ShaderNodeMapping")
    n_map.location = (x0+200, y0)

    #link
    links = mat.node_tree.links
    links.new(n_tc.outputs["Object"], n_map.inputs["Vector"])


    return

#%%registration
def register():
    #independent
    spiking_neuron()

def unregister():
    pass