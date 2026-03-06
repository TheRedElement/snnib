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
    
    Attributes
        - TODO
        
    Inferred Attributes
        - TODO
        
    Methods
        - TODO
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
        if bpy.context.scene.network_container is None:
            self.network_container = bpy.context.active_object
        else:
            self.network_container              = bpy.context.scene.network_container
        self.axon_length                    = bpy.context.scene.snnib_props.axon_length
        self.n_neurons                      = bpy.context.scene.snnib_props.n_neurons
        self.p_synapses                     = bpy.context.scene.snnib_props.p_synapses
        self.synapse_max_nonconnections     = bpy.context.scene.snnib_props.synapse_max_nonconnections
        self.synapse_maxlen_nonconnections  = bpy.context.scene.snnib_props.synapse_maxlen_nonconnections
        self.synapse_resolution             = bpy.context.scene.snnib_props.synapse_resolution
        self.seed                           = bpy.context.scene.snnib_props.seed
        self.voxel_size                     = bpy.context.scene.snnib_props.voxel_size
        
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
        coords = utils.random.random_points_bbox(self.network_container, self.Rng, self.n_neurons)
        #TODO (actual inside): coords = utils.random.random_points_raycast(self.network_container, self.Rng, self.n_neurons)
        
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
    
    def draw_neurons(self,
        template_obj:bpy.types.Object=None,
        ):
        """draws neurons into the scene
        
        - uses `template_obj` to instantiate neurons based on `template_obj`
            - creates new `template_obj` if `None`
        """

        name_template = "SNNIB.Neuron.Template"

        #default params
        if template_obj is None:
            #call custom operator
            template_obj = generate_template_neuron(name_template)

            #parenting
            template_obj.parent = self.network_container          
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
            
            #instantiation
            neuron_obj = bpy.data.objects.new(neuron_idx, template_obj.data)
            neuron_obj.location = self.coords[n]
            
            #add to network neurons
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
            neuron_gn = utils.geo_nodes_utils.copy_geonodes(template_obj, neuron_obj)
            neuron_gn = [mod for mod in neuron_obj.modifiers if mod.type == 'NODES'][0]     #first geonodes modifier of the template object
            
            socket_mapping = {item.name:item.identifier for item in neuron_gn.node_group.interface.items_tree}
            neuron_gn[socket_mapping["Axon Curve"]] = axon_obj
            neuron_gn[socket_mapping["Spiketrain"]] = bpy.data.images["SpikeTrain.Main.001"]
                        
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
            pre_neuron = self.neuron_objects[int(synapse[0])]
            pre_axon = self.axon_objects[int(synapse[0])]
            post_neuron = self.neuron_objects[int(synapse[1])]
            
            pre_axon_data = pre_axon.data
            
            offset = post_neuron.location - pre_neuron.location
            _ = utils.mesh_utils.add_spline2data(
                pre_axon_data,
                coords=np.linspace(
                    pre_axon_data.splines[0].bezier_points[-1].co,  #last point of axon-root
                    pre_axon_data.splines[0].bezier_points[-1].co + offset,
                    self.synapse_resolution,
                ),
            )
            
            #add some random branching
            axon_verts = np.array([bp.co for spline in pre_axon_data.splines for bp in spline.bezier_points[1:-1]])
            for sncidx in range(self.synapse_max_nonconnections):
                
                branch_root_idx = self.Rng.integers(0, len(axon_verts)-1)                       #index of vertex to branch off of
                branch_root = axon_verts[branch_root_idx]                                       #vertex to branch off of                

                """TODO: direction constraint
                direction = (axon_verts[branch_root_idx] - branch_root)                         #local direction of connection
                direction /= np.linalg.norm(direction)                                          #normalize
                direction += ((self.Rng.random(3)-0.5) * 0.3)                                   #add variation to direction to allow growth away from root
                direction /= np.linalg.norm(direction)                                          #normalize to avoid scaling issues
                """
                direction = 1.0
                _ = utils.mesh_utils.add_spline2data(
                    pre_axon_data,
                    coords=np.linspace(
                        branch_root,
                        branch_root + (self.Rng.random(3) - 0.5) * self.synapse_maxlen_nonconnections * direction,
                        self.synapse_resolution
                    )
                )
                
                #update axon_verts
                axon_verts = np.array([bp.co for spline in pre_axon_data.splines for bp in spline.bezier_points[1:-1]])
            
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
    gn.node_group = bpy.data.node_groups["SnnibNeuronNeurites"]

    return neuron_obj



#%%registering
def register():
    pass

def unregister():
    pass
