"""
FormCraft - Plaster Mold Generator for Blender
Generates slip-casting style plaster mold boxes from 3D models.
"""

bl_info = {
    "name": "FormCraft",
    "author": "",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > N-Panel > FormCraft",
    "description": "Generate slip-casting plaster molds with registration keys",
    "category": "Object",
    "doc_url": "https://github.com/YOUR_USERNAME/formcraft_addon",
}

if "bpy" in locals():
    import importlib
    importlib.reload(properties)
    importlib.reload(geometry)
    importlib.reload(updater)
    importlib.reload(operators)
    importlib.reload(ui)
else:
    from . import properties
    from . import geometry
    from . import updater
    from . import operators
    from . import ui

import bpy


def register():
    properties.register()
    operators.register()
    ui.register()


def unregister():
    ui.unregister()
    operators.unregister()
    properties.unregister()


if __name__ == "__main__":
    register()
