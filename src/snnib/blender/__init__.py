"""submodules that are only working within [blender](https://www.blender.org/)

- ONLY WORKS WITHIN BLENDER
- add-on to generate/visualize spiking neural networks in blender
- conventions
    - follow  [blender](https://www.blender.org/)s [best practices](https://docs.blender.org/api/current/info_best_practice.html)
    - classes: `CATEGORY_<type>T_<name>`

Modules
- `geo_nodes`
- `network`
- `operators`
- `panels`
- `properties`
- `shader_nodes`
- `spiketrain`

Subpackages
- `utils` -- utility functions to efficiently deal with specific [blender](https://www.blender.org/) objects

    
LICENSE:
MIT License

Copyright (c) 2026 Lukas Steinwender
lukas.steinwender99+snnib@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""


#%%imports
import bpy

from .. import DEV, bl_info #global constants (necessary for bpy module)

#submodules
from . import (
    network,
    geo_nodes,
    shader_nodes,
    opreators,
    panels,
    properties,
)
modules = (
    network,
    # geo_nodes,
    # shader_nodes,   #NOTE: might have to be loaded BEFORE `geo_nodes`
    opreators,
    panels,
    properties,
)

import importlib

# ignore_modules = (geo_nodes,)
ignore_modules = []


#%%registering
def register():
    for m in modules:
        if m not in ignore_modules:
            m.register()


def unregister():
    for m in modules:
        if m not in ignore_modules:
            m.unregister()

if "bpy" in locals():
    for m in modules:
        importlib.reload(m)
