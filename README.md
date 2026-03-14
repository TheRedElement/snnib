# SNNIB: Spiking Neural Networks Into Blender

![](gfx/snnib_logo.svg)

* this add-on consists of two parts
    * a python package used create files compatible with `SNNIB`
    * the blender add-on

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
|Imported [brian2](https://briansimulator.org/) network| Randomly Generated Network|
| :-: | :-: |
|![](./renders/SnnibBrian2Tiny0001-0120.gif) | ![](./renders/SnnibRandom0001-0120.gif) |

## Quickstart

> more detailed documentation can be found in the [readthedocs page](https://snnib.readthedocs.io/en/latest/index.html)

### Add-on
#### Installation
1. download [snnib.zip](./snnib.zip)
2. in [blender](https://blender.org/)
    1. navigate to `Edit > Preferences > Add-ons`
    2. drag and drop the downloaded file ([snnib.zip](./snnib.zip)) into the window
    3. click `OK`

#### Navigation
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

## TODO:
- [ ] add example animations to README.md
- [ ] readthedocs
    - separate quickstart
    - add tutorials
- [ ] save function (to store network randomly generated with `snnib`)
