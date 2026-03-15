# SNNIB: Spiking Neural Networks Into Blender

![](gfx/snnib_logo.svg)

<!-- local table of contents -->
```{contents} Table of Contents
:local:
:depth: 3
```

<!-- block -->
> [!NOTE]
> this add-on consists of two parts:
> the blender add-on;
> a python package used create files compatible with `SNNIB`;
<!-- block -->

* if you find this add-on useful in your work, an acknowledgement would be appreciated:
```latex
@software{PY_Steinwender2026_snnib,
	author    = {{Steinwender}, Lukas},
	title     = {SNNIB: Spiking Neural Network Into Blender},
	month     = Mar,
	year      = 2026,
	version   = {latest},
	url       = {https://github.com/TheRedElement/snnib.git}
}
```

## Example Renders
|||
| :-: | :-: |
|![](renders/SnnibRandom0001-0120.gif)|![](renders/SnnibBrian2Tiny0001-0120.gif)|
| randomly generated network | imported [brian2](https://briansimulator.org/) network ([source](https://github.com/TheRedElement/snnib/raw/refs/heads/main/data/brian2_tiny.json))|
|![](renders/SnnibBrian2Small0001-0120.gif)||
|imported [brian2](https://briansimulator.org/) network (400 neurons, 1260 synapses, [source](https://github.com/TheRedElement/snnib/raw/refs/heads/main/data/brian2_small.json)) | |

<!-- block -->
> [!NOTE]
> you can also render much larger networks depending on your hardware.
> on a 16GB RAM, 16 core laptop I tested up to 1600 neurons.
> The main issue you will run into is that there is so much going on, that it is hard to distinguish individual neurons and neurites.
<!-- block -->

## Quickstart

> more detailed documentation can be found in the [readthedocs page](https://snnib.readthedocs.io/en/latest/index.html)

### Add-on
#### Installation
1. download [releases/snnib.zip](https://github.com/TheRedElement/snnib/raw/refs/heads/main/releases/snnib.zip)
2. in [blender](https://blender.org/)
    1. navigate to `Edit > Preferences > Add-ons`
    2. drag and drop the downloaded file ([snnib.zip](https://github.com/TheRedElement/snnib/raw/refs/heads/main/releases/snnib.zip)) into the window
    3. click `OK`

#### Navigation

||||
|:-:|:-:|:-:|
|![](./gfx/SnnibTutorialUiRandom.gif)|![](./gfx/SnnibTutorialFromFile.gif)|![](./gfx/SnnibTutorialGeoNodes.gif)|
|generating random network|loading network from file|control using geometry nodes|

1. in `Viewport Display` expand the right side panel (by hitting `n`)
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
5. **make sure to `Apply Scale` on the `Network Container` (and potentially also the `Template Neuron`)**
6. hit `Build SNN` to generate your network

#### Mappings
* one time-step ($dt$) in a SNN simulation is mapped to a single frame in blender

### Python package
#### Installation
* simply install via `pip`
```bash
pip3 install git+https://github.com/TheRedElement/snnib.git
```

for tutorials checkout [tutorials](./tutorials.md)


## Currently supported simulators
* random network generation
* [brian2](https://briansimulator.org/)

## For developers
### Compiling the add-on
If you want to compile the add-on yourself (i.e., in case you made some changes to a forked repo and want to compile an updated version) you can do so by calling the following from the repository root:
```bash
bash publish.sh
```

## Known Restrictions
* because a lot of geometry is generated when building a large network, `crtl + z` will likely fail

## TODO:
- [ ] geo nodes node trees and shader nodes node trees do not persist when reloading the `.blend` file
- [ ] save function (to store network randomly generated with `snnib`)
