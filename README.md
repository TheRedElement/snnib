# SNNIB: Spiking Neural Networks Into Blender


## TODO:
- [ ] testing
- [ ] tutorials
- [x] refactor spiketrain material generation (module "spiketrains.py") 
- [x] implement random spiketrain generation for random network
- [x] reimplement network generation with new geonodes setup
- [x] build [shader node tree](./src/snnib/shader_nodes.py)

## Quickstart
1. in `Viewport Display` expand the right side panel (`Ctrl+n`)
2. initialization (only needs to be done once right after loading)
    1. run all the operators in the `Actions > Initialization` box in order
        1. done by clicking the respective buttons
        2. necessary to have all building blocks for a functioning network available
3. generate a `Template Neuron`
    1. will be used as source to instance neurons in your network
    2. it is recommended to use the generated template neuron and adjust it to your liking via the associated `Geometry Nodes` modifier
        1. you just need to modify the `Geometry Nodes` on the template neuron as all changes will be reflected on all instances
4. adjust the `Settings`
    1. provide a `Network Container`
        1. I recommend a cuboid because the add-on uses the objects bounding box to define the neuron positions
    2. adjust the remaining settings or styling in the `Template Neuron`s `Geometry Nodes`
5. **make sure to `Apply Scale` on the `Network Container` (and potentially also the `Template Neuron`)
6. hit `Build SNN` to generate your network

## Mappings
* one time-step ($dt$) in a SNN animation is mapped to a single frame in blender

## Currently supported simulators
* random network generation
* [brian2](https://briansimulator.org/)


## FAQ
### `Network Container` does not transform to a wireframe when hitting `Build SNN`
#### Cause 1: Deleted `Geometry Nodes` group
* most likely you have deleted and re-generated the necessary `Geometry Nodes` group which leads to
    * `Network Container` still has the `Geometry Nodes` modifier attached but no `node tree` linked anymore
        * behaves as if no `Geometry Nodes` applied at all

Solution 1:
> delete the `Geometry Nodes` modifier and hit `Build SNN` again
Solution 2:
> copy the nodes from `SnnibNetworkContainer` into the associated `Geometry Nodes` modifier
