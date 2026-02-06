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
        snnib_collection:bpy.types.Collection,
        coords:np.ndarray=None,
        synapses:np.ndarray=None,
        ):
        """constructor
        
        Parameters
            - `snnib_collection`
                - `bpy.types.Collection`
                - collection to create network inside of
            - `coords`
                - `np.ndarray`, optional
                - coordinates of the neurons contained in the network
                - 3d
                    - axis 0 is to number of neurons
                    - axis 1 is `3`
                        - `x`
                        - `y`
                        - `z`
                - the default is `None`
                    - will generate a random network
            - `synapses`
                - `np.ndarray`
                - synapses present in the network
                - 3d
                    - axis 0 is to number of synapses
                    - axis 1 is `3`
                        - index of presynaptic neuron
                        - index of postsynaptic neuron
                        - synaptic weight
                - the default is `None`
                    - will generate a random network
        
                
        Raises
        
        Returns
        
        """
        
        #user input
        self.n_neurons = bpy.context.scene.snnib_props.n_neurons
        self.p_synapses = bpy.context.scene.snnib_props.p_synapses
        self.seed       = bpy.context.scene.snnib_props.seed
        self.Rng = np.random.default_rng(seed=self.seed)
        
        #attributes
        self.snnib_collection = snnib_collection
        
        if coords is None or synapses is None:
            #generate random network 
            self.generate_network()
        else:
            #TODO: read from file
            self.coords = coords
            self.synapses = synapses
            self.n_neurons = len(coords)
            self.n_synapses = len(synapses)
            self.p_synapses = self.n_synapses / self.n_neurons**2
            
        #infered attributes
        self.neuron_collection = None
        
        
        return
    
    def generate_network(self,
        ):
        """generates random network based on user input
        """
        
        #generate neurons at random locations
        coords = (self.Rng.random((self.n_neurons,3)) - 0.5) * 10

        #generate random synapses
        synapses = self.Rng.random((self.n_neurons,self.n_neurons))             #synapse weight
        synapses *= (self.Rng.random(synapses.shape) < self.p_synapses)      #connection probability
        connected = (synapses > 0)
        synapses = np.append(np.transpose(np.where(connected)), synapses[connected].reshape(-1,1), axis=1)
              
        #set attributes
        self.coords = coords
        self.synapses = synapses
        self.n_synapses = len(synapses)
        
        return
    
    def draw_neurons(self,
        template_obj:bpy.types.Object=None,
        neuron_collection:bpy.types.Collection=None,
        axon_collection:bpy.types.Collection=None,
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
            self.template_collection = utils.collection_utils.ensure_collection("Templates", self.snnib_collection)
            self.template_collection.objects.link(template_obj)
        else:
            template_obj = template_obj
        if neuron_collection is None:
            self.neuron_collection = utils.collection_utils.ensure_collection("Neurons", self.snnib_collection)
        else:
            self.neuron_collection = collection
        if axon_collection is None:
            self.axon_collection = utils.collection_utils.ensure_collection("Axons", self.snnib_collection)
        else:
            self.axon_collection = collection
            
                
        #generating instances
        for n in range(self.n_neurons):
            #create new neuron based on `template_obj`
            neuron_idx = f"Neuron.{n:04d}"
            axon_idx = f"Axon.{n:04d}"
            
            ########
            #NEURON#
            ########
            """
            #generation (non-linked copy)
            neuron_obj = template_obj.copy()
            neuron_obj.name = neuron_idx            
            neuron_obj.data = template_obj.data.copy()
            neuron_obj.data.name = neuron_idx
            neuron_obj.location = self.coords[n]
            """
            
            #instanciation
            neuron_obj = bpy.data.objects.new(neuron_idx, template_obj.data)
            neuron_obj.location = self.coords[n]
            
            
            #unlink from all current collections
            utils.collection_utils.obj_unlink_all_collections(neuron_obj)

            #add to neuron collection            
            self.neuron_collection.objects.link(neuron_obj)            
            
            ######
            #AXON#
            ######
            #init neurons axon
            neuron_verts = neuron_obj.data.vertices
            axon_data = bpy.data.curves.new(name=axon_idx, type='CURVE')
            axon_data.dimensions = '3D'
            _ = utils.mesh_utils.add_spline2data(
                axon_data,
                coords=[
                    neuron_obj.location,
                    neuron_obj.location + 1.5*neuron_verts[self.Rng.integers(0, len(neuron_verts))].co,  #connection point of axon in random direction
                ],
            )
            
            ##create object
            axon_obj = bpy.data.objects.new(axon_idx, axon_data)
            self.axon_collection.objects.link(axon_obj)
            
        
            #copy geonodes
            # utils.geo_nodes_utils.copy_geonodes(template_obj, neuron_obj)
            neuron_gn = utils.geo_nodes_utils.copy_geonodes(template_obj, neuron_obj)
            neuron_gn = neuron_obj.modifiers["GeometryNodes"]
            neuron_gn["Socket_5"] = axon_obj    #not sure why `Socket_5`
            
            #add remesh modifier to merge geometry
            neuron_remesh = neuron_obj.modifiers.new(f"Remesh_{neuron_obj.name}", 'REMESH')
        
        return
    
    def draw_synapses(self,
        ):
        """draws synapses into the scene
        """
    
        #create synapses (additional splines appended to axon that connect to postsynaptic neuron)
        for s in range(self.n_synapses):
            #synapse parameters
            synapse = self.synapses[s]
            pre_neuron = bpy.data.objects.get(f"Neuron.{synapse[0]:04.0f}")
            pre_axon = bpy.data.objects.get(f"Axon.{synapse[0]:04.0f}")
            post_neuron = bpy.data.objects.get(f"Neuron.{synapse[1]:04.0f}")
            
            
            pre_axon_data = pre_axon.data
            _ = utils.mesh_utils.add_spline2data(
                pre_axon_data,
                coords=[
                    pre_axon_data.splines[0].bezier_points[-1].co,  #last point of axon-root
                    np.random.rand(3),  #connection point of axon in random direction
                ],
            )
            logger.debug(type(pre_axon_data))
            

            
            """TODO
            #add hook modifer (to link synapse start and end to neuron positions)
            mod = pre_neuron.modifiers.new(f"Hook_{pre_neuron.name}.{s:03d}", 'HOOK')
            mod.object = post_neuron                #set parent
            mod.vertex_indices_set([v_post_idx])    #set influenced vertices
            #mod.center = neuron_obj.location
            mod.center = pre_neuron.matrix_world.inverted() @ post_neuron.matrix_world.translation            
            """
            
            """
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
