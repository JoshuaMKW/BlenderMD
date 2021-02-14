import subprocess
import sys
import tempfile
from os import getenv
from os import sep as PATH_SEP
from pathlib import Path

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, StringProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper

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


class ImportBMD(bpy.types.Operator, ImportHelper):
    """Save an BMD Mesh file"""
    bl_idname = "import_mesh.bmd"
    bl_label = "Import BMD Mesh"
    filter_glob = StringProperty(
        default="*.bmd",
        options={"HIDDEN"},
    )

    check_extension = True
    filename_ext = ".bmd"

    # execute() is called by blender when running the operator.
    def execute(self, context):
        bmdPath = Path(self.filepath)
        dest = Path(tempfile.gettempdir(), "BlenderMD", bmdPath.stem + ".dae").resolve()
        dest.mkdir(parents=True, exist_ok=True)
        superPath = Path(context.preferences.addons[__name__].preferences.superPath)

        subprocess.run([str(superPath), str(bmdPath), str(dest)])

        # Import our .dae model
        bpy.ops.wm.collada_import(filepath=str(dest))

        # this lets blender know the operator finished successfully.
        return {"FINISHED"}


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
        fbxPath = Path(self.filepath).with_suffix(".fbx")
        superPath = Path(context.preferences.addons[__name__].preferences.superPath)

        # Export out model as fbx
        bpy.ops.export_scene.fbx(filepath=str(fbxPath))

        parameters = ""  # Stuff like mat and that
        if self.rot:
            parameters = "--rotate"
        parameters += f" {self.otherParams}"
        parameters = parameters.strip().split(" ")

        subprocess.run([str(superPath), str(fbxPath), *parameters])
        fbxPath.unlink()
        # this lets blender know the operator finished successfully.
        return {"FINISHED"}


__classes__ = (ImportBMD,
               ExportBMD,
               BMDPathPreference)  # list of classes to register/unregister


def register():
    from bpy.utils import register_class, unregister_class
    for cls in __classes__:
        register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_import)  # Add to export menu
    bpy.types.TOPBAR_MT_file_export.append(menu_export)  # Add to export menu


def menu_import(self, context):
    self.layout.operator(ImportBMD.bl_idname,
                         text="Gamecube/Wii model (.bmd)")


def menu_export(self, context):
    self.layout.operator(ExportBMD.bl_idname,
                         text="Gamecube/Wii model (.bmd)")


def unregister():
    from bpy.utils import register_class, unregister_class
    for cls in reversed(__classes__):
        unregister_class(cls)
    bpy.types.TOPBAR_MT_file_import.remove(menu_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_export)


# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == "__main__":
    register()
