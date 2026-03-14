"""base class and function to create a `SNNIB` network

- exposed (and called) via blender UI elements
- controls the look of the generated network

Exceptions

Classes
    - `Network` -- container of the `SNNIB` network

Functions
    - `generate_template_neuron()` -- generates a template neuron and adds it to the scene

Other Objects
"""

#%%imports
import bpy
import bmesh

import importlib
import json
import logging
import numpy as np
from typing import List

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from snnib import scaling
from . import utils
from . import spiketrain

importlib.reload(utils)
importlib.reload(spiketrain)


#%%definitions
class Network:
    """container representing a spiking neural network
    
    Attributes
        - `network_container` -- container defining the boundaries of the `SNNIB` network inside [blender](https://www.blender.org/)
        - `template_neuron` -- object serving as template for all neurons in the network
        - `network_file` -- `SNNIB` compatible file representing a network output from a simulation
        
    Inferred Attributes
        - `axon_length`
            - `float`
            - length of the axon root
            - axon only starts to branch out after that point
            - obtained from [blender](https://www.blender.org/) UI
        - `axon_objects`
            - `List[bpy.types.Object]`
            - objects of all axons that are part of the network
        - `n_neurons`
            - `int`
            - number of neurons contained in the network
            - obtained from [blender](https://www.blender.org/) UI
            - only relevant for randomly generated network
        - `neuron_objects`
            - `List[bpy.types.Object]`
            - objects of all neurons that are part of the network
        - `p_synapses`
            - `float`
            - probability of a synapse forming between any two neurons
            - obtained from [blender](https://www.blender.org/) UI
            - only relevant for randomly generated network
        - `p_spike`
            - `float`
            - probability of a neuron spiking at any time
                - i.e., on for every neuron for every frame `p_spike` a spike is emitted with probability `p_spike`
            - obtained from [blender](https://www.blender.org/) UI
            - only relevant for randomly generated network
        - `Rng`
            - `np.random.Generator`
            - random number generator to use for network generation
        - `seed`
            - `int`
            - random seed
            - obtained from [blender](https://www.blender.org/) UI
            - only relevant for randomly generated network
        
    Methods
        - `_get_mean_outconnection()` -- returns mean direction of outgoing connections of some neuron
        - `generate_network()` -- generates a random network
        - `read_network()` -- loads a network from a file
        - `setup_container()` -- sets up the network container
        - `draw_neurons()` -- creates neurons and adds them to the scene
        - `draw_synapses()` -- creates outgoing connections and ads them to the scene

    Dependencies
        - `bpy`
        - `bmesh`
        - `json`
        - `logging`
        - `numpy`
        - `typing`
    """
    
    def __init__(self,
        network_container:bpy.types.Object,
        template_neuron:bpy.types.Object,
        network_file:str=None,
        ):
        """constructor
        
        - generates a random network if no `network_file` was found
        - otherwise reads the network from `network_file`

        Parameters
            - `network_container`
                - `bpy.types.Object`
                - object representing the network container in the scene
                - bounding box of `network_container` defines the region the network will occupy
                    - neuron coordinates will be remapped to lie within the bounding box
            - `template_neuron`
                - `bpy.types.Object`
                - object representing a template to use for every neuron contained in the network
                    - neurons in the network are instanced from `template_neuron`
                - you only need to modify `template_neuron` in order to procedurally apply the changes to all neurons in the network
            - `network_file`
                - `str`, optional
                - file containing a save network to load into `SNNIB`
                - the default is `None`
                    - use random generation instead of reading from a file
                
        Raises
        
        Returns
        """
        
        #user input
        self.network_container = network_container
        self.template_neuron = template_neuron
        if network_file in [None,""]: self.network_file = None
        else: self.network_file = network_file

        #scene attributes
        self.axon_length                    = bpy.context.scene.snnib_props.axon_length
        self.n_neurons                      = bpy.context.scene.snnib_props.n_neurons
        self.p_spike                        = bpy.context.scene.snnib_props.p_spike
        self.p_synapses                     = bpy.context.scene.snnib_props.p_synapses
        self.seed                           = bpy.context.scene.snnib_props.seed
        
        #get RNG
        self.Rng = np.random.default_rng(seed=self.seed)
        if self.network_file is None:
            #generate random network 
            logger.info(f"generating random network")
            self.generate_network()
        else:
            #read from file
            logger.info(f"reading {self.network_file}")
            self.read_network()
            
        #inferred attributes
        self.neuron_objects = []
        self.axon_objects = []
        
        return
    
    def _get_mean_outconnection(self,
        pre_idx:int,
        ) -> np.ndarray:
        """returns vector describing the direction of mean outgoing connection from neuron `pre_idx`

        - returns random direction if no outgoing connections

        Parameters
            - `pre_idx`
                - `int`
                - index of the neuron to compute the direction for

        Raises

        Returns
            -`direction`
                - `np.ndarray`
                - mean direction of outgoing connections
        """

        #get postsynaptic neurons
        post_idxs = [int(s_out["post"]) for s_out in filter(lambda s: s["pre"]==pre_idx, self.synapses)]
        
        if len(post_idxs) == 0:
            #random direction
            direction = self.Rng.random(3) - 0.5           #random direction
        else:
            #compute mean connection direction
            direction = np.array([(self.neurons[pn]["coords"]-self.neurons[pre_idx]["coords"]) for pn in post_idxs]).mean(axis=0)
        
        return direction

    def generate_network(self,):
        """generates random network based on user input

        - will
            - generate random coordinates within `self.network_container`s bounding box
            - generate random spiketrains for every neuron
                - for every frame there is a probability `self.p_spike` to emit a spike
            - generate random connections between neurons
                - for every pair of neurons a connections exists with probability `self.p_synapses`
            - generate metadata corresponding to the render settings

        Parameters

        Raises

        Returns
        """
      
        #generate neurons at random locations
        coords = utils.random.random_points_bbox(self.network_container, self.Rng, self.n_neurons)
        #TODO (actual inside): coords = utils.random.random_points_raycast(self.network_container, self.Rng, self.n_neurons)

        #generate random spikes
        n_frames = bpy.context.scene.frame_end - bpy.context.scene.frame_start
        spiketrains = [[
            frame for frame in range(n_frames) if (self.Rng.random() < self.p_spike)       #check if spike occurred at current frame
        ] for n in range(len(coords))]

        #generate random synapses
        synapses = self.Rng.random((self.n_neurons,self.n_neurons))         #synapse weight
        synapses *= (self.Rng.random(synapses.shape) < self.p_synapses)     #connection probability
        synapses *= (1-np.eye(self.n_neurons,self.n_neurons))               #prevent self-connection (for now)
        connected = (synapses > 0)
        synapses = np.append(np.transpose(np.where(connected)), synapses[connected].reshape(-1,1), axis=1)
              
        #set attributes
        self.meta = dict(
            t_sim=n_frames, t_sim_unit="frame",
            dt=1, dt_unit="frame",
            steps=n_frames,
        )
        self.neurons = [dict(coords=coords[n], spiketrain=spiketrains[n]) for n in range(self.n_neurons)]
        self.synapses = [dict(pre=s[0], post=s[1], w=s[2]) for s in synapses]
        self.n_synapses = len(synapses)
        logger.debug(self.neurons[0])
        logger.debug(self.synapses[0])
        return
    
    def read_network(self):
        """reads a network from `self.network_file`

        - will
            - read the network elements and parameters
            - map the contained neuron coordinates to `self.network_container`s bounding box

        Parameters

        Raises

        Returns        
        """
        #get context locations
        bb_min, bb_max = utils.mesh_utils.get_bbox(self.network_container)
        
        with open(self.network_file, "r") as f:
            data = json.load(f)
            
            #read and adjust coordinates to bbox
            coords = np.array([[n[0],n[1],n[2]] for n in data["neurons"]])
            coords = scaling.minmaxscale(coords, bb_min, bb_max, axis=0)
            self.neurons = [dict(
                coords=coords[nidx],
                spiketrain=set(np.round(n[3],0).astype(int)))
            for nidx, n in enumerate(data["neurons"])]
            self.meta = data["meta"]
            self.synapses = [dict(pre=s[0], post=s[1], w=s[2]) for s in data["synapses"]]
            self.n_neurons = len(self.neurons)
            self.n_synapses = len(self.synapses)
            self.p_synapses = self.n_synapses / self.n_neurons**2
            logger.debug(self.neurons[0])
            logger.debug(self.synapses[0])
        return
    
    def setup_container(self):
        """sets up the network container

        - will
            - clear all children of `self.container`
            - add the respective geo nodes node tree
        
        Parameters

        Raises

        Returns
        """

        logger.info(f"setting up network container")

        #initial cleanup
        logger.warning(f"clearing children of network container")
        for child in self.network_container.children_recursive:
            bpy.data.objects.remove(child, do_unlink=True)          

        #add geonodes (if none existent)
        if len([mod for mod in self.network_container.modifiers if mod.type=='NODES']) == 0:
            gn = self.network_container.modifiers.new(name="Network.Container", type='NODES')
            gn.node_group = bpy.data.node_groups["SnnibNetworkContainer"]
        
        #other settings
        self.network_container.hide_render = True
    
        return
    
    def draw_neurons(self,):
        """draws neurons into the scene
        
        - will
            - instantiate neurons based on `self.template_neuron`
            - initialize axons (axon roots)
            - apply geo nodes inputs
            - adjust geo nodes mappings (to roughly match actual simulation)
        
        Parameters

        Raises

        Returns        
        """
        logger.info(f"drawing {self.n_neurons} neurons")

        #generating instances
        for n in range(self.n_neurons):
            #create new neuron based on `self.template_neuron`
            neuron_idx = f"Neuron"
            axon_idx = f"Axon"
            
            ########
            #NEURON#
            ########
            
            #instantiation
            neuron_obj = bpy.data.objects.new(neuron_idx, self.template_neuron.data)
            neuron_obj.location = self.neurons[n]["coords"]
            # neuron_obj.rotation_euler = self.Rng.uniform(0, 2*np.pi, 3)  #random orientation
            # utils.mesh_utils.apply_rotation(neuron_obj)
            
            #add to network neurons
            self.neuron_objects.append(neuron_obj)

            ######
            #AXON#
            ######
            #get axon direction
            # axon_direction = self.Rng.random(3) - 0.5           #random direction
            # axon_direction = np.array([0,0,1])                  #in z
            axon_direction = self._get_mean_outconnection(n)       #mean outgoing connection
            axon_direction /= np.linalg.norm(axon_direction)    #normalize

            
            #init neurons axon
            neuron_verts = neuron_obj.data.vertices
            axon_data = bpy.data.curves.new(name=axon_idx, type='CURVE')
            axon_data.dimensions = '3D'
            _ = utils.mesh_utils.add_spline2data(
                axon_data,
                coords=[
                    (0,0,0),    #because child of neuron
                    axon_direction * 0.6 * self.axon_length,               #always in z (neuron rotation controls actual orientation)
                    axon_direction * 1.0 * self.axon_length,               #always in z (neuron rotation controls actual orientation)
                ],
                scale=0.1,  #small scale to make sure other outgoing connections have the same root
                handle_type='ALIGNED',
            )
            
            ##create object
            axon_obj = bpy.data.objects.new(axon_idx, axon_data)
            self.axon_objects.append(axon_obj)


            #copy geonodes
            neuron_gn = utils.geo_nodes_utils.copy_geonodes(self.template_neuron, neuron_obj)
            neuron_gn = [mod for mod in neuron_obj.modifiers if mod.type == 'NODES'][0]                         #first geonodes modifier of the template object
            socket_mapping = {item.name:item.identifier for item in neuron_gn.node_group.interface.items_tree}  #map sockets to name for easy access
            
            ##set geonodes inputs
            neuron_gn[socket_mapping["Axon Curve"]] = axon_obj
            # neuron_gn[socket_mapping["Spiketrain"]] = bpy.data.images["SpikeTrain.Main.001"]    #TODO: adjust
            neuron_gn[socket_mapping["Spiketrain"]] = spiketrain.make_spike_texture(
                spike_steps=self.neurons[n]["spiketrain"], steps=self.meta["steps"],
                img_name=f"Spiketrain.{neuron_obj.name}",
                override=False,
            )
            ##adjust geonodes mapping
            neuron_gn[socket_mapping["Seed"]] = int(self.Rng.integers(0,10000))  #make sure every set of dendrites in unique
            gn_steps_node = utils.geo_nodes_utils.get_node_by_label(neuron_gn.node_group, "Number of Simulation Steps")
            gn_steps_node.outputs["Value"].default_value = self.meta["steps"]
            gn_st_stretch = utils.geo_nodes_utils.get_node_by_label(neuron_gn.node_group, "SpikeTrain.Stretch")
            gn_st_stretch.outputs["Value"].default_value = self.meta["t_sim"]/self.meta["steps"]    #equivalent to `self.meta["dt"]`
            
            #parenting
            axon_obj.parent = neuron_obj
            neuron_obj.parent = self.network_container
            
            for obj in [neuron_obj, axon_obj]:
                #add to scene (link to all collections that the parent is in)
                for col in self.network_container.users_collection:
                    col.objects.link(obj)
            
        return
    
    def draw_synapses(self,):
        """draws synapses into the scene
        
        - will
            - add spline to respective axon object for every existing synapse

        Parameters

        Raises

        Returns           
        """

        logger.info(f"drawing {self.n_synapses} synapses")

        #create synapses (additional splines appended to axon that connect to postsynaptic neuron)
        for s in range(self.n_synapses):
            #synapse parameters
            synapse = self.synapses[s]
            pre_neuron = self.neuron_objects[int(synapse["pre"])]
            pre_axon = self.axon_objects[int(synapse["pre"])]
            post_neuron = self.neuron_objects[int(synapse["post"])]
            offset = post_neuron.location - pre_neuron.location     #destination relative to `pre_neuron`

            pre_axon_data = pre_axon.data
            axon_root_points = [bp.co for bp in pre_axon_data.splines[0].bezier_points]
            
            _ = utils.mesh_utils.add_spline2data(
                pre_axon_data,      #add another outgoing connection to the axon (new, detached spline)
                coords=[
                    *axon_root_points,      #start the same as the axon root
                    offset,                 #target point
                ],
                scale=[
                    *[0.1]*len(axon_root_points),
                    0.5,
                ],
                handle_type=[
                    *['ALIGNED']*len(axon_root_points),
                    'ALIGNED',
                ],
            )
            
        return

def generate_template_neuron(
    name:str,
    ) -> bpy.types.Object:
    """returns generated template neuron object
    
    - will
        - generate a template neuron
            - create a cube
            - convert to a sphere
            - add respective geometry nodes (as a single user copy)
        - add the object (with name `name`) to the scene

    Parameters
        - `name`
            - `str`
            - name to use for the template neuron

    Raises

    Returns
        - `neuron_obj`
            - `bpy.types.Object`
            - generated neuron object
    """

    #create cube
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, 0),
    )
    neuron_obj = bpy.context.active_object
    neuron_obj.name = name
    neuron_obj.data.name = name

    #convert to sphere
    radius = .5
    bm = bmesh.new()
    bm.from_mesh(neuron_obj.data)
    bmesh.ops.subdivide_edges(  #subdivide
        bm,
        edges=bm.edges,
        cuts=5,
        use_grid_fill=True,
    )
    for v in bm.verts:          #convert to sphere (all vertices at constant radius from object origin)
        v.co = v.co.normalized() * radius
    
    bm.to_mesh(neuron_obj.data)
    bm.free()

    #add geonodes
    gn = neuron_obj.modifiers.new(name="Neuron.Axon", type='NODES')
    gn.node_group = bpy.data.node_groups["SnnibNeuronNeurites"].copy()  #make single user copy of node group

    return neuron_obj



#%%registering
def register():
    pass

def unregister():
    pass
