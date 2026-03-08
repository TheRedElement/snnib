"""
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
logging.basicConfig(level=logging.DEBUG)

from . import utils
from . import spiketrain

importlib.reload(utils)
importlib.reload(spiketrain)


#%%definitions
class Network:
    """container representing a spiking neural network
    
    Attributes
        - TODO
        
    Inferred Attributes
        - TODO
        
    Methods
        - TODO
    """
    
    def __init__(self,
        network_container:bpy.types.Object,
        template_neuron:bpy.types.Object,
        network_file:str=None,
        # neurons:List[dict]=None,
        # synapses:np.ndarray=None,
        ):
        """constructor
        
        Parameters
            - 
                
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
        self.p_synapses                     = bpy.context.scene.snnib_props.p_synapses
        self.seed                           = bpy.context.scene.snnib_props.seed
        
        #get RNG
        self.Rng = np.random.default_rng(seed=self.seed)
        if self.network_file is None:
            #generate random network 
            self.generate_network()
        else:
            #TODO: read from file
            logger.info(f"reading {self.network_file}")
            self.read_network()
            
        #infered attributes
        self.neuron_objects = []
        self.axon_objects = []
        
        return
    
    def _get_mean_outconnection(self,
        pre_idx:int,
        ) -> np.ndarray:
        """returns vector of mean outgoing connection from neuron `pre_idx`

        - returns random direction if no outgoing connections
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

    def generate_network(self,
        ):
        """generates random network based on user input
        """
      
        #generate neurons at random locations
        coords = utils.random.random_points_bbox(self.network_container, self.Rng, self.n_neurons)
        #TODO (actual inside): coords = utils.random.random_points_raycast(self.network_container, self.Rng, self.n_neurons)
        #TODO: generate random spiketrains for each neuron
        n_frames = bpy.context.scene.frame_end - bpy.context.scene.frame_start
        spiketrains = [[
            frame for frame in range(n_frames) if (self.Rng.random() < bpy.context.scene.snnib_props.p_spike)       #check if spike occurred at current frame
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
        print(self.neurons[0])
        print(self.synapses[0])
        return
    
    def read_network(self):
        """reads a network from a `self.network_file`
        """
        #get context locations
        bb_min, bb_max = utils.mesh_utils.get_bbox(self.network_container)
        
        with open(self.network_file, "r") as f:
            data = json.load(f)
            
            
            #read and adjust coordinates to bbox
            coords = np.array([[n[0],n[1],n[2]] for n in data["neurons"]])
            coords = utils.scaling.minmaxscale(coords, bb_min, bb_max, axis=0)
            self.neurons = [dict(
                coords=coords[nidx],
                spiketrain=set(np.round(n[3],0).astype(int)))
            for nidx, n in enumerate(data["neurons"])]
            self.meta = data["meta"]
            self.synapses = [dict(pre=s[0], post=s[1], w=s[2]) for s in data["synapses"]]
            self.n_neurons = len(self.neurons)
            self.n_synapses = len(self.synapses)
            self.p_synapses = self.n_synapses / self.n_neurons**2
            # print(self.neurons[0])
            # print(self.synapses[0])
        return
    
    def setup_container(self):
        
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
        
        - uses `self.self.template_neuron` to instantiate neurons based on `self.self.template_neuron`
        """

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
    
    def draw_synapses(self,
        ):
        """draws synapses into the scene
        """

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

def generate_template_neuron(name:str) -> bpy.types.Object:
    """returns generated template neuron object
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
