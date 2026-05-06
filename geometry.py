"""
Core geometry generation functions for FormCraft plaster mold boxes.
"""

import bpy
import bmesh
from mathutils import Vector
from math import cos, sin, pi


def get_object_bounds(obj):
    matrix = obj.matrix_world
    bounds = [matrix @ Vector(b) for b in obj.bound_box]
    xs = [b.x for b in bounds]
    ys = [b.y for b in bounds]
    zs = [b.z for b in bounds]
    return (
        Vector((min(xs), min(ys), min(zs))),
        Vector((max(xs), max(ys), max(zs))),
    )


def create_rounded_box_mesh(context, width, depth, height, corner_radius):
    mesh = bpy.data.meshes.new("FormCraftMoldBox")
    bm = bmesh.new()

    w = width / 2
    d = depth / 2
    h = height / 2
    r = min(corner_radius, w * 0.4, d * 0.4)
    seg = 4

    profile = []

    if r > 0.001:
        arc_pts = max(2, seg)
        for i in range(arc_pts + 1):
            a = pi + (pi / 2) * (i / arc_pts)
            profile.append((w - r + r * cos(a), d - r + r * sin(a)))
        for i in range(arc_pts + 1):
            a = pi / 2 + (pi / 2) * (i / arc_pts)
            profile.append((-w + r + r * cos(a), d - r + r * sin(a)))
        for i in range(arc_pts + 1):
            a = 0 + (pi / 2) * (i / arc_pts)
            profile.append((-w + r + r * cos(a), -d + r + r * sin(a)))
        for i in range(arc_pts + 1):
            a = -pi / 2 + (pi / 2) * (i / arc_pts)
            profile.append((w - r + r * cos(a), -d + r + r * sin(a)))
    else:
        profile = [
            (w, d),
            (-w, d),
            (-w, -d),
            (w, -d),
        ]

    verts = [bm.verts.new((x, y, -h)) for x, y in profile]
    verts_top = [bm.verts.new((x, y, h)) for x, y in profile]

    n = len(verts)
    for i in range(n):
        bm.faces.new([verts[i], verts[(i + 1) % n],
                       verts_top[(i + 1) % n], verts_top[i]])

    bm.faces.new(list(reversed(verts)))
    bm.faces.new(verts_top)

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("FormCraftMoldBox", mesh)
    context.collection.objects.link(obj)
    return obj


def create_mold_box(context, master_obj, settings):
    bbox_min, bbox_max = get_object_bounds(master_obj)

    size = bbox_max - bbox_min
    center = (bbox_max + bbox_min) / 2

    inner_w = size.x + settings.margin * 2
    inner_d = size.y + settings.margin * 2
    inner_h = size.z + settings.margin

    if settings.square_box:
        outer_base = max(inner_w, inner_d) + settings.wall_thickness * 2
        outer_w = outer_base
        outer_d = outer_base
    else:
        outer_w = inner_w + settings.wall_thickness * 2
        outer_d = inner_d + settings.wall_thickness * 2

    outer_h = inner_h + settings.base_thickness

    box_obj = create_rounded_box_mesh(
        context, outer_w, outer_d, outer_h, settings.corner_radius
    )
    box_obj.location = center + Vector((0, 0, -settings.base_thickness / 2))
    context.view_layer.update()

    return box_obj, center, (outer_w, outer_d, outer_h), (inner_w, inner_d, inner_h)


def boolean_subtract(context, target_obj, cutter_obj, modifier_name="Boolean"):
    mod = target_obj.modifiers.new(name=modifier_name, type="BOOLEAN")
    mod.object = cutter_obj
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"

    context.view_layer.objects.active = target_obj
    bpy.ops.object.modifier_apply(modifier=mod.name)


def create_cylinder_mesh(radius, depth, segments=16):
    mesh = bpy.data.meshes.new("Cylinder")
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=True,
        segments=segments,
        diameter1=radius,
        diameter2=radius,
        depth=depth,
    )
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def create_pouring_hole(context, mold_obj, center, box_dims, settings):
    if not settings.add_pouring_hole:
        return

    hole_mesh = create_cylinder_mesh(
        settings.pouring_hole_radius, box_dims[2] * 2, 16
    )
    hole_obj = bpy.data.objects.new("PouringHole", hole_mesh)
    hole_obj.location = Vector((center.x, center.y, center.z))
    context.collection.objects.link(hole_obj)

    boolean_subtract(context, mold_obj, hole_obj, "PouringHole")
    bpy.data.objects.remove(hole_obj)


def create_vent_channels(context, mold_obj, center, box_dims, settings, inner_dims):
    if not settings.add_vents:
        return

    radius = settings.vent_radius
    vent_height = box_dims[2] * 0.8
    offset_x = (inner_dims[0] / 2) * 0.9
    offset_y = (inner_dims[1] / 2) * 0.9

    vent_positions = [
        (center.x + offset_x, center.y + offset_y),
        (center.x - offset_x, center.y + offset_y),
        (center.x + offset_x, center.y - offset_y),
        (center.x - offset_x, center.y - offset_y),
    ]

    for i, (vx, vy) in enumerate(vent_positions):
        vent_mesh = create_cylinder_mesh(radius, vent_height * 2, 8)
        vent_obj = bpy.data.objects.new(f"Vent_{i}", vent_mesh)
        vent_obj.location = Vector((vx, vy, center.z))
        context.collection.objects.link(vent_obj)

        boolean_subtract(context, mold_obj, vent_obj, f"Vent_{i}")
        bpy.data.objects.remove(vent_obj)


def split_mesh_by_plane(obj, axis, split_value):
    mesh = obj.data

    upper_bm = bmesh.new()
    upper_bm.from_mesh(mesh)

    lower_bm = bmesh.new()
    lower_bm.from_mesh(mesh)

    plane_no = Vector((1, 0, 0))
    if axis == "Z":
        plane_no = Vector((0, 0, 1))
    elif axis == "Y":
        plane_no = Vector((0, 1, 0))

    plane_co = Vector((0, 0, 0))
    if axis == "Z":
        plane_co.z = split_value
    elif axis == "Y":
        plane_co.y = split_value
    else:
        plane_co.x = split_value

    bmesh.ops.bisect_plane(
        upper_bm,
        geom=upper_bm.verts[:] + upper_bm.edges[:] + upper_bm.faces[:],
        dist=0.0001,
        plane_co=plane_co,
        plane_no=plane_no,
        use_cap_fill=False,
        clear_inner=True,
    )

    bmesh.ops.bisect_plane(
        lower_bm,
        geom=lower_bm.verts[:] + lower_bm.edges[:] + lower_bm.faces[:],
        dist=0.0001,
        plane_co=plane_co,
        plane_no=plane_no,
        use_cap_fill=False,
        clear_outer=True,
    )

    for bm in [upper_bm, lower_bm]:
        bmesh.ops.dissolve_limit(
            bm, angle_limit=0.01, verts=bm.verts, edges=bm.edges,
        )

    upper_mesh = bpy.data.meshes.new("UpperHalf")
    lower_mesh = bpy.data.meshes.new("LowerHalf")
    upper_bm.to_mesh(upper_mesh)
    lower_bm.to_mesh(lower_mesh)
    upper_bm.free()
    lower_bm.free()

    return upper_mesh, lower_mesh


def split_mold(context, mold_obj, settings, center):
    axis = settings.split_axis

    bbox_min, bbox_max = get_object_bounds(mold_obj)

    if axis == "Z":
        split_val = (bbox_min.z + bbox_max.z) / 2
    elif axis == "Y":
        split_val = (bbox_min.y + bbox_max.y) / 2
    else:
        split_val = (bbox_min.x + bbox_max.x) / 2

    upper_mesh, lower_mesh = split_mesh_by_plane(mold_obj, axis, split_val)

    half_a = bpy.data.objects.new("FormCraftMold_Top", upper_mesh)
    half_b = bpy.data.objects.new("FormCraftMold_Bottom", lower_mesh)
    context.collection.objects.link(half_a)
    context.collection.objects.link(half_b)

    bpy.data.objects.remove(mold_obj)
    context.view_layer.update()

    return half_a, half_b


def _create_cylinder_object(radius, depth, location, rotation, name):
    mesh = create_cylinder_mesh(radius, depth, 16)
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = rotation
    return obj


def add_registration_keys(context, mold_half, center, box_dims, inner_dims, settings, is_top_half=True):
    axis = settings.split_axis
    key_count = settings.key_count
    key_radius = settings.key_radius
    key_depth = settings.key_depth

    bbox_min, bbox_max = get_object_bounds(mold_half)

    if axis == "Z":
        face_z = bbox_max.z if is_top_half else bbox_min.z
        radius = min(inner_dims[0], inner_dims[1]) * 0.3

        for i in range(key_count):
            angle = (2 * pi * i) / key_count + pi / key_count
            kx = center.x + radius * cos(angle)
            ky = center.y + radius * sin(angle)

            loc = Vector((kx, ky, face_z))
            if is_top_half:
                loc.z -= key_depth / 2
            else:
                loc.z += key_depth / 2

            key_obj = _create_cylinder_object(
                key_radius, key_depth, loc, (0, 0, 0), f"KeyHole_{i}"
            )
            context.collection.objects.link(key_obj)
            boolean_subtract(context, mold_half, key_obj, f"KeyHole_{i}")
            bpy.data.objects.remove(key_obj)

    elif axis == "Y":
        face_y = bbox_max.y if is_top_half else bbox_min.y
        radius_x = inner_dims[0] * 0.3
        radius_z = inner_dims[2] * 0.3

        for i in range(key_count):
            angle = (2 * pi * i) / key_count
            kx = center.x + radius_x * cos(angle)
            kz = center.z + radius_z * sin(angle)

            loc = Vector((kx, face_y, kz))
            if is_top_half:
                loc.y -= key_depth / 2
            else:
                loc.y += key_depth / 2

            key_obj = _create_cylinder_object(
                key_radius, key_depth, loc, (pi / 2, 0, 0), f"KeyHole_{i}"
            )
            context.collection.objects.link(key_obj)
            boolean_subtract(context, mold_half, key_obj, f"KeyHole_{i}")
            bpy.data.objects.remove(key_obj)

    else:
        face_x = bbox_max.x if is_top_half else bbox_min.x
        radius_y = inner_dims[1] * 0.3
        radius_z = inner_dims[2] * 0.3

        for i in range(key_count):
            angle = (2 * pi * i) / key_count
            ky = center.y + radius_y * cos(angle)
            kz = center.z + radius_z * sin(angle)

            loc = Vector((face_x, ky, kz))
            if is_top_half:
                loc.x -= key_depth / 2
            else:
                loc.x += key_depth / 2

            key_obj = _create_cylinder_object(
                key_radius, key_depth, loc, (0, pi / 2, 0), f"KeyHole_{i}"
            )
            context.collection.objects.link(key_obj)
            boolean_subtract(context, mold_half, key_obj, f"KeyHole_{i}")
            bpy.data.objects.remove(key_obj)

    context.view_layer.update()
