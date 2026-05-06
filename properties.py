import bpy
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty, PointerProperty, StringProperty


class FormCraftSettings(bpy.types.PropertyGroup):
    wall_thickness: FloatProperty(
        name="Wall Thickness",
        description="Thickness of plaster walls",
        default=0.03,
        min=0.005,
        max=0.1,
        subtype="DISTANCE",
        unit="LENGTH",
    )

    margin: FloatProperty(
        name="Margin",
        description="Clearance around master object",
        default=0.02,
        min=0.0,
        max=0.1,
        subtype="DISTANCE",
        unit="LENGTH",
    )

    base_thickness: FloatProperty(
        name="Base Thickness",
        description="Thickness of mold bottom",
        default=0.02,
        min=0.005,
        max=0.1,
        subtype="DISTANCE",
        unit="LENGTH",
    )

    corner_radius: FloatProperty(
        name="Corner Radius",
        description="Radius of outer box corners",
        default=0.01,
        min=0.0,
        max=0.05,
        subtype="DISTANCE",
        unit="LENGTH",
    )

    square_box: BoolProperty(
        name="Square Box",
        description="Make outer shape square using largest dimension",
        default=True,
    )

    split_axis: EnumProperty(
        name="Split Axis",
        description="Axis to split mold along",
        items=[
            ("Z", "Z (Top/Bottom)", "Split horizontally"),
            ("Y", "Y (Front/Back)", "Split vertically front to back"),
            ("X", "X (Left/Right)", "Split vertically left to right"),
        ],
        default="Z",
    )

    split_mold: BoolProperty(
        name="Split Into Halves",
        description="Split mold into two halves",
        default=True,
    )

    key_count: IntProperty(
        name="Key Count",
        description="Number of registration keys per side",
        default=4,
        min=2,
        max=12,
    )

    key_radius: FloatProperty(
        name="Key Radius",
        description="Radius of registration keys",
        default=0.006,
        min=0.002,
        max=0.03,
        subtype="DISTANCE",
        unit="LENGTH",
    )

    key_depth: FloatProperty(
        name="Key Depth",
        description="Depth of registration keys",
        default=0.012,
        min=0.003,
        max=0.05,
        subtype="DISTANCE",
        unit="LENGTH",
    )

    add_pouring_hole: BoolProperty(
        name="Pouring Hole",
        description="Add pouring hole to top of mold",
        default=True,
    )

    pouring_hole_radius: FloatProperty(
        name="Pouring Hole Radius",
        description="Radius of pouring hole",
        default=0.008,
        min=0.002,
        max=0.05,
        subtype="DISTANCE",
        unit="LENGTH",
    )

    add_vents: BoolProperty(
        name="Vent Channels",
        description="Add small vent channels for air escape",
        default=True,
    )

    vent_radius: FloatProperty(
        name="Vent Radius",
        description="Radius of vent channels",
        default=0.002,
        min=0.001,
        max=0.01,
        subtype="DISTANCE",
        unit="LENGTH",
    )

    non_destructive: BoolProperty(
        name="Non-Destructive",
        description="Keep original object and use modifiers instead of applying",
        default=False,
    )

    work_on_copy: BoolProperty(
        name="Work on Copy",
        description="Duplicate master object before generating mold",
        default=True,
    )


class FormCraftPreferences(bpy.types.AddonPreferences):
    bl_idname = "formcraft_addon"

    github_repo: StringProperty(
        name="GitHub Repository",
        description="Owner/repo (e.g. yourname/formcraft_addon)",
        default="",
    )

    use_prereleases: BoolProperty(
        name="Include Pre-Releases",
        description="Check pre-release versions for updates",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "github_repo")
        layout.prop(self, "use_prereleases")


classes = [
    FormCraftSettings,
    FormCraftPreferences,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.formcraft = bpy.props.PointerProperty(type=FormCraftSettings)
    bpy.types.Scene.formcraft_update_message = bpy.props.StringProperty(
        name="Update Message",
        default="",
    )
    bpy.types.Scene.formcraft_update_version = bpy.props.StringProperty(
        name="Update Version",
        default="",
    )
    bpy.types.Scene.formcraft_update_zip_path = bpy.props.StringProperty(
        name="Update ZIP Path",
        default="",
        subtype="FILE_PATH",
    )


def unregister():
    del bpy.types.Scene.formcraft_update_zip_path
    del bpy.types.Scene.formcraft_update_version
    del bpy.types.Scene.formcraft_update_message
    del bpy.types.Scene.formcraft
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
