"""
"""

#%%imports
import bpy
import bmesh

import importlib
import logging
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

from . import utils


#%%definitions
class Network:
    """container representing a spiking neural network
    """
    
    def __init__(self,
        bsnn_collection:bpy.types.Collection,
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
            
            #generation (non-linked copy)
            neuron_obj = template_obj.copy()
            neuron_obj.name = neuron_idx            
            neuron_obj.data = template_obj.data.copy()
            neuron_obj.data.name = neuron_idx
            neuron_obj.location = self.coords[n]
            
            """#instanciation
            neuron_obj = bpy.data.objects.new(neuron_idx, template_obj.data)
            neuron_obj.location = self.coords[n]
            """
            
            #copy geonodes
            utils.geo_nodes_utils.copy_geonodes(template_obj, neuron_obj)
            
            #unlink from all current collections
            utils.collection_utils.obj_unlink_all_collections(neuron_obj)

            #add to neuron collection            
            self.neuron_collection.objects.link(neuron_obj)
        
        return
    
    def draw_axons(self,
        ):
        """draws synapses into the scene
        """
        
        #create synapses
        for s in range(self.n_synapses):
            #synapse parameters
            synapse_idx = f"Synapse.{s:04d}"
            synapse = self.synapses[s]
            pre_neuron = bpy.data.objects.get(f"Neuron.{synapse[0]:04.0f}")
            post_neuron = bpy.data.objects.get(f"Neuron.{synapse[1]:04.0f}")          

            #select neuron to manipulate (pre = root of axon)
            bpy.ops.object.select_all(action='DESELECT')
            pre_neuron.select_set(True)
            bpy.context.view_layer.objects.active = pre_neuron

            #get most-aligned vertex
            offset = post_neuron.matrix_world.translation - pre_neuron.matrix_world.translation
            direction = offset.normalized()
            
            best_v_idx = None
            best_score = 1e-20
            for idx, v in enumerate(pre_neuron.data.vertices):
                vec = v.co - pre_neuron.location
                score = vec.dot(direction)
                if score > best_score:
                    best_score = score
                    best_v_idx = idx
                    
            if best_v_idx is None:
                logger.debug("TODO: autapse (self-connection)")
                #TODO: self connection
                continue
            
            
            #extrude vertex
            mesh = pre_neuron.data
            mesh.vertices.add(1)
            v_post_idx = len(mesh.vertices) - 1
            v_post = mesh.vertices[v_post_idx]
            v_post.co += offset
            mesh.edges.add(1)
            mesh.edges[-1].vertices = (best_v_idx, v_post_idx)
            
            """TODO
            #add hook modifer (to link synapse start and end to neuron positions)
            mod = pre_neuron.modifiers.new(f"Hook_{pre_neuron.name}.{s:03d}", 'HOOK')
            mod.object = post_neuron                #set parent
            mod.vertex_indices_set([v_post_idx])    #set influenced vertices
            #mod.center = neuron_obj.location
            mod.center = pre_neuron.matrix_world.inverted() @ post_neuron.matrix_world.translation
            """
            
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
