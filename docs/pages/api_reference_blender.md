<!-- NOTE: :recursive: -> show all children as well (to display all methods when summarizing class) -->


# API Reference (Blender Add-On)

```{eval-rst}
.. currentmodule:: snnib.blender
```

## snnib.blender

```{eval-rst}
.. autosummary::
    :signatures: short
    :recursive:
    :toctree: tocBlender/

    blender
```

### utils
```{eval-rst}
.. autosummary::
    :signatures: short
    :recursive:
    :toctree: tocBlender/

    utils
```

#### collection_utils

```{eval-rst}
.. autosummary::
    :signatures: short
    :recursive:
    :toctree: tocBlender/

    utils.collection_utils
    utils.collection_utils.ensure_collection
    utils.collection_utils.clear_collection
    utils.collection_utils.obj_unlink_all_collections
```
#### geo_nodes_utils

```{eval-rst}
.. autosummary::
    :signatures: short
    :recursive:
    :toctree: tocBlender/
    
    utils.geo_nodes_utils
    utils.geo_nodes_utils.add_todo_node
    utils.geo_nodes_utils.copy_geonodes
    utils.geo_nodes_utils.clear_node_group
    utils.geo_nodes_utils.create_node_group
    utils.geo_nodes_utils.delete_geonode_groups
    utils.geo_nodes_utils.exists_node_group
    utils.geo_nodes_utils.get_node_by_label
    utils.geo_nodes_utils.set_node_curve

    utils.mesh_utils.add_spline2data
    utils.mesh_utils.apply_rotation
    utils.mesh_utils.get_bbox

    utils.random.random_points_bbox
    utils.random.random_points_raycast
```

#### mesh_utils

```{eval-rst}
.. autosummary::
    :signatures: short
    :recursive:
    :toctree: tocBlender/
    
    utils.mesh_utils
    utils.mesh_utils.add_spline2data
    utils.mesh_utils.apply_rotation
    utils.mesh_utils.get_bbox

    utils.random.random_points_bbox
    utils.random.random_points_raycast
```

#### random

```{eval-rst}
.. autosummary::
    :signatures: short
    :recursive:
    :toctree: tocBlender/
    
    utils.random
    utils.random.random_points_bbox
    utils.random.random_points_raycast
```


### geo_nodes
```{eval-rst}
.. autosummary::
    :signatures: short
    :recursive:
    :toctree: tocBlender/

    geo_nodes
    geo_nodes.network_container
    geo_nodes.neurite_bends
    geo_nodes.neurite_branches
    geo_nodes.neurite_to_mesh
    geo_nodes.neurite_twist
    geo_nodes.neuron_neurites
    geo_nodes.position_global
    geo_nodes.remesh
    geo_nodes.scale_radial
    geo_nodes.spiketrain

```

### network

```{eval-rst}
.. autosummary::
    :signatures: short
    :recursive:
    :toctree: tocBlender/

    network
```

```{eval-rst}
.. autosummary::
    :signatures: short
    :recursive:
    :toctree: tocBlender/

    network
    network.Network
    network.Network.__init__
    network.Network._get_mean_outconnection
    network.Network.generate_network
    network.Network.read_network
    network.Network.setup_container
    network.Network.draw_neurons
    network.Network.draw_synapses
```

```{eval-rst}
.. autosummary::
    :signatures: short
    :recursive:
    :toctree: tocBlender/

    network.generate_template_neuron
```

### operators

```{eval-rst}
.. autosummary::
    :signatures: short
    :recursive:
    :toctree: tocBlender/

    operators
    operators.SNNIB_OT_build_snn
    operators.SNNIB_OT_build_snn.execute
    operators.SNNIB_OT_make_template_neuron
    operators.SNNIB_OT_make_template_neuron.execute
    operators.SNNIB_OT_init_geo_nodes
    operators.SNNIB_OT_init_geo_nodes.execute
    operators.SNNIB_OT_init_shader_nodes
    operators.SNNIB_OT_init_shader_nodes.execute

```

### panels

```{eval-rst}
.. autosummary::
    :signatures: short
    :recursive:
    :toctree: tocBlender/

    panels
    panels.SNNIB_PT_Panel
```

### properties

```{eval-rst}
.. autosummary::
    :signatures: short
    :recursive:
    :toctree: tocBlender/

    properties
    properties.SnnibProperties
```

### shader nodes

```{eval-rst}
.. autosummary::
    :signatures: short
    :recursive:
    :toctree: tocBlender/

    shader_nodes
    shader_nodes.spiking_neuron
```

### spiketrain

```{eval-rst}
.. autosummary::
    :signatures: short
    :recursive:
    :toctree: tocBlender/

    spiketrain
    shader_nodes.make_spike_texture
```
