def format_code(codes, indent_level):
    s = ""
    for c in codes:
        s += '    ' * indent_level + c + '\n'
    return s

def do_add(tokens, indent_level=1):
    if tokens[0] == "SPHERE":
        codes = []
        codes.append("add_sphere('PrimObj')")
        msg = "Add sphere"
        codes.append(f"print(\"{msg}\")")
    elif tokens[0] == "CUBE":
        codes = []
        codes.append("add_cube('PrimObj')")
        msg = "Add cube"
        codes.append(f"print(\"{msg}\")")
    return format_code(codes, indent_level)

def _loop_face_threshold_vert_co(ax, op):
    codes = \
f"""
for f in bm.faces:
    f.select = True
    for v in f.verts:
        if not v.co[{ax}] {op} threshold:
            f.select = False
            break
    
"""
    return codes.split('\n')

def do_select(tokens, indent_level=1):
    codes = []
    # deselect all 
    codes.append("obj = bpy.data.objects['PrimObj']")
    codes.append("bpy.context.view_layer.objects.active = obj")
    codes.append("if bpy.context.active_object.mode != 'EDIT': bpy.ops.object.editmode_toggle()")
    codes.append("bpy.ops.mesh.select_all(action='DESELECT')")
    codes.append("me = obj.data")
    codes.append("bm = bmesh.from_edit_mesh(me)")
    codes.append("bm.faces.ensure_lookup_table()")

    if tokens[0] == "FACE":
        if tokens[1] == "LOCATION":
            # compute the bounding box
            # https://blender.stackexchange.com/questions/8459/get-blender-x-y-z-and-bounding-box-with-script
            codes.append("from mathutils import Vector")
            codes.append("bbox_corners = [obj.matrix_world @ Vector(corner) " +
                "for corner in obj.bound_box]")
            # bbox is the bounding box
            t = float(tokens[3])
            if tokens[2] in ["UP", "DOWN"]:
                # criterion: z
                ax = 2
            elif tokens[2] in ["LEFT", "RIGHT"]:
                ax = 0
            elif tokens[2] in ["Y+", "Y-"]:
                ax = 1
            if tokens[2] in ["UP", "RIGHT", "Y+"]:
                comp_op = ">"
                t = 10 - t
            else:
                comp_op = "<"
            codes.append(f"bb = [v[{ax}] for v in bbox_corners]")
            codes.append("vmax = max(bb); vmin = min(bb)")
            t = t / 10.0  
            codes.append(f"threshold = vmin + (vmax - vmin) * {t}")
            codes += _loop_face_threshold_vert_co(ax, comp_op)
    else:
        raise ValueError("Unsupported select", tokens[0])

    codes.append("bmesh.update_edit_mesh(me)")

    return format_code(codes, indent_level)

def do_inset(tokens, indent_level=1):
    thick = float(tokens[0]) / 10.0
    depth = float(tokens[1]) / 10.0
    codes = []
    codes.append(f"bpy.ops.mesh.inset(thickness={thick}, depth={depth})")
    return format_code(codes, indent_level)

def do_resize(tokens, indent_level=1):
    codes = []
    if tokens[1] == "+":
        s = float(tokens[2]) / 10.0 + 1.0
    elif tokens[1] == "-":
        s = 1.0 - float(tokens[2]) / 10.0
    if tokens[0] == 'ALL':
        codes.append(f"bpy.ops.transform.resize(value=({s}, {s}, {s}), "\
            "orient_type='GLOBAL', "
            "orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), "
            "orient_matrix_type='GLOBAL')") #, mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=False, use_snap_edit=False, use_snap_nonedit=False, use_snap_selectable=False)")
        

    elif tokens[0] == "X":
        codes.append(f"bpy.ops.transform.resize(value=({s}, 1, 1),"
            " orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=False, use_snap_edit=False, use_snap_nonedit=False, use_snap_selectable=False)")
    elif tokens[0] == "Y":
        codes.append(f"bpy.ops.transform.resize(value=(1, {s}, 1),"
            " orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=False, use_snap_edit=False, use_snap_nonedit=False, use_snap_selectable=False)")
    elif tokens[0] == "Z":
        codes.append(f"bpy.ops.transform.resize(value=(1, 1, {s}),"
            " orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=False, use_snap_edit=False, use_snap_nonedit=False, use_snap_selectable=False)")
    else:
        raise ValueError("not implemented")

    return format_code(codes, indent_level)

def do_delete(tokens, indent_level=1):
    codes=["bpy.ops.mesh.delete(type='FACE')"]
    return format_code(codes, indent_level)

def do_mod_solidify(tokens, indent_level=1):
    codes = []
    codes.append("obj = bpy.data.objects['PrimObj']")
    codes.append("bpy.context.view_layer.objects.active = obj")
    codes.append("me = obj.data")
    codes.append("bpy.ops.object.mode_set(mode='OBJECT')")
    codes.append("bpy.ops.object.modifier_add(type='SOLIDIFY')")
    codes.append("bpy.context.object.modifiers['Solidify'].use_even_offset = True")
    thick = float(tokens[0]) * .05
    codes.append(f"bpy.context.object.modifiers['Solidify'].thickness = {thick}")
    codes.append("bpy.ops.object.modifier_apply(modifier='Solidify')")
    # codes.append("bpy.ops.object.convert(target='MESH')")
    return format_code(codes, indent_level)

def do_object_mode(tokens, indent_level=1):
    codes = []
    codes.append("bpy.context.view_layer.objects.active = bpy.data.objects['PrimObj']")
    codes.append("bpy.ops.object.mode_set(mode='OBJECT')")
    return format_code(codes, indent_level)

def do_edit_mode(tokens, indent_level=1):
    codes = []
    codes.append("bpy.context.view_layer.objects.active = bpy.data.objects['PrimObj']")
    codes.append("bpy.ops.object.mode_set(mode='EDIT')")
    return format_code(codes, indent_level)

def gen_bl_code(script_code, indent_level=1):
    bl_code = ""
    for l in script_code.split('\n'):
        tokens = l.split(' ')
        if tokens[0] == "ADD":
            bl_code += do_add(tokens[1:], indent_level)
        if tokens[0] == "SELECT":
            bl_code += do_select(tokens[1:], indent_level)
        if tokens[0] == "INSET":
            bl_code += do_inset(tokens[1:], indent_level)
        if tokens[0] == "RESIZE":
            bl_code += do_resize(tokens[1:], indent_level)
        if tokens[0] == "DELETE":
            bl_code += do_delete(tokens[1:], indent_level)
        if tokens[0] == "OBJECT_MODE":
            bl_code += do_object_mode([], indent_level)
        if tokens[0] == "EDIT_MODE":
            bl_code += do_edit_mode([], indent_level)
        if tokens[0] == "MOD_SOLIDIFY":
            bl_code += do_mod_solidify(tokens[1:], indent_level)

    return bl_code # print(bl_code)