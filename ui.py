import bpy


class FORMCRAFT_PT_panel(bpy.types.Panel):
    bl_label = "FormCraft"
    bl_idname = "FORMCRAFT_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FormCraft"

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.operator("formcraft.import_file", text="Import", icon="IMPORT")
        row.operator("formcraft.export_stl", text="Export", icon="EXPORT")
        row.operator("formcraft.reset_project", text="Reset", icon="FILE_REFRESH")
        row.operator("formcraft.new_project", text="New", icon="FILE_NEW")

        layout.separator()

        layout.operator(
            "formcraft.generate_mold",
            text="Generate Mold",
            icon="MOD_BOOLEAN",
        )

        layout.separator()

        box = layout.box()
        box.label(text="Box Settings", icon="CUBE")
        box.prop(settings, "square_box")
        box.prop(settings, "wall_thickness")
        box.prop(settings, "margin")
        box.prop(settings, "base_thickness")
        box.prop(settings, "corner_radius")

        box = layout.box()
        box.label(text="Split", icon="UNLINKED")
        box.prop(settings, "split_mold")
        if settings.split_mold:
            box.prop(settings, "split_axis")

        box = layout.box()
        box.label(text="Registration Keys", icon="MESH_CIRCLE")
        box.prop(settings, "key_count")
        box.prop(settings, "key_radius")
        box.prop(settings, "key_depth")

        box = layout.box()
        box.label(text="Pouring", icon="OUTLINER_OB_LIGHT")
        box.prop(settings, "add_pouring_hole")
        if settings.add_pouring_hole:
            box.prop(settings, "pouring_hole_radius")
        box.prop(settings, "add_vents")
        if settings.add_vents:
            box.prop(settings, "vent_radius")

        box = layout.box()
        box.label(text="Workflow", icon="PREFERENCES")
        box.prop(settings, "work_on_copy")
        box.prop(settings, "non_destructive")

        layout.separator()
        layout.operator(
            "formcraft.export_stl",
            text="Export as STL",
            icon="EXPORT",
        )

        layout.separator()

        update_box = layout.box()
        update_box.label(text="Updates", icon="FILE_REFRESH")

        version_info = context.scene.formcraft_update_message
        version_str = context.scene.formcraft_update_version

        if version_info:
            icon = "INFO" if version_str else "ERROR"
            update_box.label(text=version_info, icon=icon)

        row = update_box.row(align=True)
        row.operator(
            "formcraft.check_update",
            text="Check for Updates",
            icon="URL",
        )
        row.operator(
            "formcraft.update_addon",
            text="Install Update",
            icon="IMPORT",
        )

        update_box.operator(
            "formcraft.install_local",
            text="Install from Local ZIP",
            icon="FILE_FOLDER",
        )


def register():
    bpy.utils.register_class(FORMCRAFT_PT_panel)


def unregister():
    bpy.utils.unregister_class(FORMCRAFT_PT_panel)
