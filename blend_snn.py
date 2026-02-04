"""
"""

#%%imports
import bpy

import importlib
import logging
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from . import utils


#%%definitions
class Network:
    """container representing a spiking neural network
    """
    
    def __init__(self,
        bsnn_collection:bpy.types.Collection,
        times:np.ndarray,
        coords:np.ndarray,
        synapses:np.ndarray,
        ):
        """constructor
        
        Parameters
            - `bsnn_collection`
                - `bpy.types.Collection`
                - collection to create network inside of
            - `times`
                - `np.ndarray`
                - times of the network simulation
            - `coords`
                - `np.ndarray`
                - coordinates of the neurons contained in the network
                - 3d
                    - axis 0 is to number of neurons
                    - axis 1 is `3`
                        - `x`
                        - `y`
                        - `z`
            - `synapses`
                - `np.ndarray`
                - synapses present in the network
                - 3d
                    - axis 0 is to number of synapses
                    - axis 1 is `3`
                        - index of presynaptic neuron
                        - index of postsynaptic neuron
                        - synaptic weight
        
                    
                
        Raises
        
        Returns
        
        """
            
        self.bsnn_collection = bsnn_collection
        self.times = times
        self.coords = coords
        self.synapses = synapses
        
        #infered attributes
        self.n_neurons = len(coords)
        self.n_synapses = len(synapses)
        self.neuron_collection = None
        
        
        return
    
    def draw_neurons(self,
        template_obj:bpy.types.Object=None,
        collection:bpy.types.Collection=None,
        ):
        """draws neurons into the scene
        
        - uses `template_obj` to instantiate neurons based on `template_obj`
            - creates new `template_obj` if `None`
        """
        #default params
        if template_obj is None:
            bpy.ops.mesh.primitive_uv_sphere_add(location=(0,0,0))
            template_obj = bpy.context.active_object
            template_obj.name = "Neuron.Template"
            template_obj.data.name = "Neuron.Template"
            
            utils.collection_utils.obj_unlink_all_collections(template_obj)
            self.template_collection = utils.collection_utils.ensure_collection("Templates", self.bsnn_collection)
            self.template_collection.objects.link(template_obj)
        else:
            template_obj = template_obj
        if collection is None:
            self.neuron_collection = utils.collection_utils.ensure_collection("Neurons", self.bsnn_collection)
        else:
            self.neuron_collection = collection
            
        #generating instances
        for n in range(self.n_neurons):
            #instantiate new neuron based on `template_obj`
            neuron_idx = f"Neuron.{n:04d}"
            neuron_obj = bpy.data.objects.new(neuron_idx, template_obj.data)
            neuron_obj.location = self.coords[n]
            
            #copy geonodes
            utils.geo_nodes_utils.copy_geonodes(template_obj, neuron_obj)
            
            #unlink from all current collections
            utils.collection_utils.obj_unlink_all_collections(neuron_obj)

            #add to neuron collection            
            self.neuron_collection.objects.link(neuron_obj)
        
        return
    
    def draw_synapses(self,
        collection:bpy.types.Collection=None,    
        ):
        """draws synapses into the scene
        """
        
        #default params
        if collection is None:
            self.synapse_collection = utils.collection_utils.ensure_collection("Synapses", self.bsnn_collection)
        else:
            self.synapse_collection = collection
                    
        #create synapses
        for s in range(self.n_synapses):
            #synapse parameters
            synapse_idx = f"Synapse.{s:04d}"
            synapse = self.synapses[s]
            pre_neuron = bpy.data.objects.get(f"Neuron.{synapse[0]:04.0f}")
            post_neuron = bpy.data.objects.get(f"Neuron.{synapse[1]:04.0f}")          

            #generate mesh
            synapse_mesh = bpy.data.meshes.new(synapse_idx)
            synapse_mesh.from_pydata(
                [pre_neuron.matrix_world.translation, post_neuron.matrix_world.translation],    #use global translation to ensure vertecies are exactly at neuron positions
                [(0,1)],
                [],
            )
            synapse_mesh.update()
            
            #link mesh to 
            synapse_obj = bpy.data.objects.new(synapse_idx, synapse_mesh)
            
            #unlink from all current collections
            utils.collection_utils.obj_unlink_all_collections(synapse_obj)

            #add to synapse collection            
            self.synapse_collection.objects.link(synapse_obj)        
            
            #add hook modifer (to link synapse start and end to neuron positions)
            for i, neuron_obj in enumerate([pre_neuron, post_neuron]):
                mod = synapse_obj.modifiers.new(f"Hook_{synapse_obj.name}.{i:03d}", 'HOOK')
                mod.object = neuron_obj             #set parent
                mod.vertex_indices_set([i])         #set influenced vertecies
                #mod.center = neuron_obj.location
                mod.center = synapse_obj.matrix_world.inverted() @ neuron_obj.matrix_world.translation
                
            
        return

#%%definitions


#%%registering
def register():

    #custom objects
    bpy.types.Scene.template_neuron = bpy.props.PointerProperty(
        name="Template Neuron",
        type=bpy.types.Object
    )



def unregister():
    
    #custom objects
    del bpy.types.Scene.template_neuron
