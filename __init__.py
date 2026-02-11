"""add-on to generate/visualize spiking neural networks

Notes
- https://docs.blender.org/api/current/index.html
- conventions:
    - https://docs.blender.org/api/current/info_best_practice.html
    - classes: `CATEGORY_<type>T_<name>`

    
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

bl_info = {
    "name": "SNNIB",
    "author": "Lukas Steinwender",
    "version": (0, 1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > My Tab",
    "description": "Spiking Neural Networks Into Blender",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "category": "3D View",
}

#%%imports

import bpy  #always first

import importlib

#submodules
from . import (
    network,
    geo_nodes,
    opreators,
    panels,
    properties,
)
modules = (
    network,
    geo_nodes,
    opreators,
    panels,
    properties,
)

ignore_modules = (geo_nodes,)
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

