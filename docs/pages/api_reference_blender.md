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

## network

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

    network.generate_template_neuron
```