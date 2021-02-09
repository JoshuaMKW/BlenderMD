import subprocess
import sys
from os import getenv
from pathlib import Path

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, StringProperty
from bpy_extras.io_utils import ExportHelper

bl_info = {
    "name": "Export BMD with SuperBMD",
    "author": "Augs",
    "version": (2, 2, 0),
    "blender": (2, 80, 0),
    "location": "File > Export > Gamecube/Wii model (.bmd)",
    "description": "This script allows you do export bmd files quickly using SuperBMD directly from blender",
    "warning": "Will overwrite an fbx file of the same name as the bmd that you are exporting",
    "category": "Import-Export"
}


class BMDPathPreference(bpy.types.AddonPreferences):
    bl_idname = __name__

    superPath: bpy.props.StringProperty(
        name="Path",
        description="Path to SuperBMD.exe",
        default="",
        maxlen=255,
        subtype="FILE_PATH"
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text='Path to SuperBMD.exe')
        row = layout.row()
        row.prop(self, 'superPath', expand=True)

class ExportBMD(bpy.types.Operator, ExportHelper):
    """Save an BMD Mesh file"""
    bl_idname = "export_mesh.bmd"
    bl_label = "Export BMD Mesh"
    filter_glob = StringProperty(
        default="*.bmd",
        options={'HIDDEN'},
    )

    check_extension = True
    filename_ext = ".bmd"

    rot: BoolProperty(
        name="Rotate",
        description="Use Z as up instead of Y",
        default=True,
    )

    otherParams: StringProperty(
        name="Other parameters",
        description="stuff like -t -s that you add to the cmd command",
        default="",
    )

    # To do: add material presets

    # execute() is called by blender when running the operator.
    def execute(self, context):
        fbxPath = Path(self.filepath).with_suffix(
            ".fbx")  # dodgy hey, changed file extension
        superPath = Path(context.preferences.addons[__name__].preferences.superPath)
        # Export out model as fbx
        bpy.ops.export_scene.fbx(filepath=str(fbxPath), path_mode="ABSOLUTE")

        parameters = ""  # Stuff like mat and that
        if self.rot:
            parameters = "--rotate"
        parameters += f" {self.otherParams}"
        parameters = parameters.strip().split(" ")

        subprocess.Popen([f'"{superPath}"', f'"{fbxPath}"', *parameters])
        fbxPath.unlink()
        # this lets blender know the operator finished successfully.
        return {"FINISHED"}


__classes__ = (ExportBMD,
               BMDPathPreference)  # list of classes to register/unregister


def register():
    from bpy.utils import register_class, unregister_class
    for cls in __classes__:
        register_class(cls)
    bpy.types.TOPBAR_MT_file_export.append(menu_export)  # Add to export menu


def menu_export(self, context):
    self.layout.operator(ExportBMD.bl_idname,
                         text="Gamecube/Wii model (.bmd)")


def unregister():
    from bpy.utils import register_class, unregister_class
    for cls in reversed(__classes__):
        unregister_class(cls)
    bpy.types.TOPBAR_MT_file_export.remove(menu_export)


# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == "__main__":
    register()
