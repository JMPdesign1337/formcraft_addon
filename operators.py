import bpy
from . import geometry
from . import updater


class FORMCRAFT_OT_generate_mold(bpy.types.Operator):
    bl_idname = "formcraft.generate_mold"
    bl_label = "Generate Plaster Mold"
    bl_description = "Generate a slip-casting style plaster mold from the selected object"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == "MESH"

    def execute(self, context):
        settings = context.scene.formcraft
        master = context.active_object

        original_master = master

        if settings.work_on_copy:
            master = master.copy()
            master.data = master.data.copy()
            master.name = "MasterCopy"
            context.collection.objects.link(master)
            context.view_layer.objects.active = master

        self.report({"INFO"}, "Generating mold box...")

        box_obj, center, box_dims, inner_dims = geometry.create_mold_box(
            context, master, settings
        )

        geometry.boolean_subtract(context, box_obj, master, "MasterCavity")

        geometry.create_pouring_hole(context, box_obj, center, box_dims, settings)
        geometry.create_vent_channels(context, box_obj, center, box_dims, settings, inner_dims)

        if not settings.work_on_copy and not settings.non_destructive:
            original_master.hide_set(True)
            original_master.hide_render = True

        if settings.split_mold:
            half_a, half_b = geometry.split_mold(context, box_obj, settings, center)

            geometry.add_registration_keys(
                context, half_a, center, box_dims, inner_dims, settings, is_top_half=True
            )
            geometry.add_registration_keys(
                context, half_b, center, box_dims, inner_dims, settings, is_top_half=False
            )
        else:
            geometry.add_registration_keys(
                context, box_obj, center, box_dims, inner_dims, settings, is_top_half=True
            )

        if settings.work_on_copy:
            master.hide_set(True)
            master.hide_render = True
        elif not settings.non_destructive:
            original_master.select_set(False)

        self.report({"INFO"}, "Mold generated successfully")
        return {"FINISHED"}


class FORMCRAFT_OT_export_stl(bpy.types.Operator):
    bl_idname = "formcraft.export_stl"
    bl_label = "Export Mold as STL"
    bl_description = "Export the generated mold halves as individual STL files"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filename: bpy.props.StringProperty(name="File Name", default="formcraft_mold")
    directory: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        import os

        directory = self.directory if self.directory else os.path.dirname(self.filepath)

        mold_objects = [
            obj for obj in context.scene.objects
            if "PlasterMold" in obj.name
        ]

        if not mold_objects:
            self.report({"WARNING"}, "No mold objects found. Generate a mold first.")
            return {"CANCELLED"}

        base_name = self.filename if self.filename else "formcraft_mold"

        for obj in mold_objects:
            obj.select_set(False)

        exported = []
        for i, obj in enumerate(mold_objects):
            obj.select_set(True)
            context.view_layer.objects.active = obj

            suffix = f"_{i + 1}" if len(mold_objects) > 1 else ""
            full_path = os.path.join(directory, f"{base_name}{suffix}.stl")

            bpy.ops.export_mesh.stl(
                filepath=full_path,
                use_selection=True,
            )
            obj.select_set(False)
            exported.append(full_path)

        self.report({"INFO"}, f"Exported {len(exported)} STL file(s)")
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class FORMCRAFT_OT_check_update(bpy.types.Operator):
    bl_idname = "formcraft.check_update"
    bl_label = "Check for Updates"
    bl_description = "Check GitHub for newer versions"

    def execute(self, context):
        prefs = context.preferences.addons.get("formcraft_addon")
        if not prefs:
            self.report({"WARNING"}, "Addon preferences not found")
            return {"CANCELLED"}

        repo = prefs.preferences.github_repo
        use_prereleases = prefs.preferences.use_prereleases

        if not repo:
            self.report({"WARNING"}, "No GitHub repository set in preferences")
            return {"CANCELLED"}

        result = updater.check_github_updates(repo, use_prereleases)
        version_info, message = result[0], result[1] if len(result) > 1 else ""

        if version_info is None:
            self.report({"INFO"}, message)
        else:
            version_str = updater.version_tuple_to_str(version_info)
            self.report({"INFO"}, f"Update available: v{version_str}")

        context.scene.formcraft_update_message = message
        context.scene.formcraft_update_version = str(version_info) if version_info else ""

        return {"FINISHED"}


class FORMCRAFT_OT_update_addon(bpy.types.Operator):
    bl_idname = "formcraft.update_addon"
    bl_label = "Update Addon"
    bl_description = "Download and install the latest version from GitHub"

    def execute(self, context):
        prefs = context.preferences.addons.get("formcraft_addon")
        if not prefs:
            self.report({"WARNING"}, "Addon preferences not found")
            return {"CANCELLED"}

        repo = prefs.preferences.github_repo
        use_prereleases = prefs.preferences.use_prereleases

        if not repo:
            self.report({"WARNING"}, "No GitHub repository set in preferences")
            return {"CANCELLED"}

        result = updater.check_github_updates(repo, use_prereleases)
        version_info, download_url = result[0], result[1]

        if version_info is None:
            self.report({"INFO"}, download_url)
            return {"CANCELLED"}

        success, message = updater.download_and_install(download_url)

        if success:
            self.report({"INFO"}, message)
        else:
            self.report({"ERROR"}, message)

        return {"FINISHED"}


class FORMCRAFT_OT_install_local(bpy.types.Operator):
    bl_idname = "formcraft.install_local"
    bl_label = "Install from Local ZIP"
    bl_description = "Install update from a local ZIP file"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filename: bpy.props.StringProperty(name="File Name", default="formcraft_addon.zip")
    directory: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        zip_path = self.filepath if self.filepath else None

        if not zip_path:
            zip_path = context.scene.formcraft_update_zip_path
            if not zip_path:
                self.report({"WARNING"}, "No ZIP file selected")
                return {"CANCELLED"}

        success, message = updater.install_local_zip(zip_path)

        if success:
            self.report({"INFO"}, message)
        else:
            self.report({"ERROR"}, message)

        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


def register():
    bpy.utils.register_class(FORMCRAFT_OT_generate_mold)
    bpy.utils.register_class(FORMCRAFT_OT_export_stl)
    bpy.utils.register_class(FORMCRAFT_OT_check_update)
    bpy.utils.register_class(FORMCRAFT_OT_update_addon)
    bpy.utils.register_class(FORMCRAFT_OT_install_local)


def unregister():
    bpy.utils.unregister_class(FORMCRAFT_OT_install_local)
    bpy.utils.unregister_class(FORMCRAFT_OT_update_addon)
    bpy.utils.unregister_class(FORMCRAFT_OT_check_update)
    bpy.utils.unregister_class(FORMCRAFT_OT_export_stl)
    bpy.utils.unregister_class(FORMCRAFT_OT_generate_mold)
