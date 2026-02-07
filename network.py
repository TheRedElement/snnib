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
        coords:np.ndarray=None,
        synapses:np.ndarray=None,
        ):
        """constructor
        
        Parameters
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
        self.network_container  = bpy.context.scene.network_container
        self.axon_length        = bpy.context.scene.snnib_props.axon_length
        self.n_neurons          = bpy.context.scene.snnib_props.n_neurons
        self.p_synapses         = bpy.context.scene.snnib_props.p_synapses
        self.seed               = bpy.context.scene.snnib_props.seed
        self.voxel_size         = bpy.context.scene.snnib_props.voxel_size
        
        #get RNG
        self.Rng = np.random.default_rng(seed=self.seed)
        
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
        self.neuron_objects = []
        self.axon_objects = []
        
        return
    
    def generate_network(self,
        ):
        """generates random network based on user input
        """
        
        #generate neurons at random locations
        min = np.array([v.co for v in self.network_container.data.vertices]).min(axis=0)
        max = np.array([v.co for v in self.network_container.data.vertices]).max(axis=0)

        coords = self.Rng.random((self.n_neurons,3)) * (max - min) + min

        #generate random synapses
        synapses = self.Rng.random((self.n_neurons,self.n_neurons))         #synapse weight
        synapses *= (self.Rng.random(synapses.shape) < self.p_synapses)     #connection probability
        synapses *= (1-np.eye(self.n_neurons,self.n_neurons))               #prevent self-connection (for now)
        connected = (synapses > 0)
        synapses = np.append(np.transpose(np.where(connected)), synapses[connected].reshape(-1,1), axis=1)
              
        #set attributes
        self.coords = coords
        self.synapses = synapses
        self.n_synapses = len(synapses)
        
        return
    
    def draw_neurons(self,
        template_obj:bpy.types.Object=None,
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
            
            #add to scene
            bpy.context.collection.objects.link(template_obj)
                    
            #parenting
            template_obj.parent = self.network_container          
                        
            # utils.collection_utils.obj_unlink_all_collections(template_obj)
            # self.template_collection = utils.collection_utils.ensure_collection("Templates", self.snnib_collection)
            # self.template_collection.objects.link(template_obj)
        else:
            template_obj = template_obj
                
        #generating instances
        for n in range(self.n_neurons):
            #create new neuron based on `template_obj`
            neuron_idx = f"Neuron"
            axon_idx = f"Axon"
            
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
            self.neuron_objects.append(neuron_obj)
            
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
                    (0,0,0),    #because child of neuron
                    (self.Rng.random(3) - 0.5) * self.axon_length
                    #in case of no parenting use neurons location
                    # neuron_obj.location,
                    # neuron_obj.location + 1.5*neuron_verts[self.Rng.integers(0, len(neuron_verts))].co,  #connection point of axon in random direction
                ],
            )
            
            ##create object
            axon_obj = bpy.data.objects.new(axon_idx, axon_data)
            self.axon_objects.append(axon_obj)
        
            #copy geonodes
            # utils.geo_nodes_utils.copy_geonodes(template_obj, neuron_obj)
            neuron_gn = utils.geo_nodes_utils.copy_geonodes(template_obj, neuron_obj)
            neuron_gn = neuron_obj.modifiers["GeometryNodes"]
            neuron_gn["Socket_5"] = axon_obj    #not sure why `Socket_5`
            
            #add remesh modifier to merge geometry
            neuron_remesh = neuron_obj.modifiers.new(f"Remesh_{neuron_obj.name}", 'REMESH')
            neuron_remesh.voxel_size = self.voxel_size
        
            #add to scene
            bpy.context.collection.objects.link(neuron_obj)
            bpy.context.collection.objects.link(axon_obj)
                    
            #parenting
            axon_obj.parent = neuron_obj
            neuron_obj.parent = self.network_container
            
        return
    
    def draw_synapses(self,
        ):
        """draws synapses into the scene
        """

        #create synapses (additional splines appended to axon that connect to postsynaptic neuron)
        for s in range(self.n_synapses):
            #synapse parameters
            synapse = self.synapses[s]
            #pre_neuron = bpy.data.objects.get(f"Neuron.{synapse[0]:04.0f}")
            #pre_axon = bpy.data.objects.get(f"Axon.{synapse[0]:04.0f}")
            #post_neuron = bpy.data.objects.get(f"Neuron.{synapse[1]:04.0f}")
            pre_neuron = self.neuron_objects[int(synapse[0])]
            pre_axon = self.axon_objects[int(synapse[0])]
            post_neuron = self.neuron_objects[int(synapse[1])]
            
            pre_axon_data = pre_axon.data
            
            offset = post_neuron.location - pre_neuron.location
            print(offset)
            _ = utils.mesh_utils.add_spline2data(
                pre_axon_data,
                coords=[
                    pre_axon_data.splines[0].bezier_points[-1].co,  #last point of axon-root
                    # np.array(pre_axon_data.splines[0].bezier_points[-1].co) + 10,
                    pre_axon_data.splines[0].bezier_points[-1].co + offset,
                ],
            )
            
        return

#%%definitions


#%%registering
def register():
    pass

def unregister():
    pass
