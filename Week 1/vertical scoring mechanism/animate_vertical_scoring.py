import bpy
import math
import os

def create_vertical_animation():
    print("=== Starting Vertical Strip Plunger Ejection 3D Model & Animation in Blender 5.2 ===")

    bpy.ops.wm.read_factory_settings(use_empty=True)

    base_dir = r"c:\FARIS\Blister Bot\Blister-bot-main-\Week 1\vertical scoring mechanism"
    vert_frames_dir = os.path.join(base_dir, "vert_frames")
    os.makedirs(vert_frames_dir, exist_ok=True)

    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.frame_start = 1
    scene.frame_end = 120
    scene.render.fps = 24

    coll = bpy.data.collections.new("VerticalScoring_Collection")
    scene.collection.children.link(coll)

    # Shaders / Materials
    def create_mat(name, color=(0.8,0.8,0.8,1.0), metallic=0.0, roughness=0.5, transmission=0.0, alpha=1.0, emission=(0,0,0,1), emission_strength=0.0):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        
        node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        if 'Base Color' in node_bsdf.inputs: node_bsdf.inputs['Base Color'].default_value = color
        if 'Metallic' in node_bsdf.inputs: node_bsdf.inputs['Metallic'].default_value = metallic
        if 'Roughness' in node_bsdf.inputs: node_bsdf.inputs['Roughness'].default_value = roughness
        if 'Transmission Weight' in node_bsdf.inputs: node_bsdf.inputs['Transmission Weight'].default_value = transmission
        elif 'Transmission' in node_bsdf.inputs: node_bsdf.inputs['Transmission'].default_value = transmission
        if 'Alpha' in node_bsdf.inputs: node_bsdf.inputs['Alpha'].default_value = alpha
        if 'Emission Color' in node_bsdf.inputs: node_bsdf.inputs['Emission Color'].default_value = emission
        elif 'Emission' in node_bsdf.inputs: node_bsdf.inputs['Emission'].default_value = emission
        if 'Emission Strength' in node_bsdf.inputs: node_bsdf.inputs['Emission Strength'].default_value = emission_strength
            
        node_output = nodes.new(type='ShaderNodeOutputMaterial')
        mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
        return mat

    mat_foil = create_mat("Mat_Foil", color=(0.9, 0.91, 0.93, 1.0), metallic=0.98, roughness=0.15)
    mat_pvc = create_mat("Mat_PVC", color=(0.9, 0.95, 1.0, 1.0), roughness=0.05, transmission=0.85, alpha=0.35)
    mat_aluminum = create_mat("Mat_Aluminum", color=(0.82, 0.84, 0.86, 1.0), metallic=0.95, roughness=0.15)
    mat_dark_metal = create_mat("Mat_DarkMetal", color=(0.2, 0.22, 0.25, 1.0), metallic=0.9, roughness=0.25)
    mat_pill_blue = create_mat("Mat_PillBlue", color=(0.0, 0.45, 0.95, 1.0), roughness=0.1)
    mat_pill_white = create_mat("Mat_PillWhite", color=(0.98, 0.98, 0.98, 1.0), roughness=0.1)
    mat_silicone = create_mat("Mat_Silicone", color=(0.95, 0.35, 0.1, 1.0), roughness=0.4)
    mat_cutter_steel = create_mat("Mat_CutterSteel", color=(0.3, 0.32, 0.35, 1.0), metallic=0.95, roughness=0.1)
    mat_led_orange = create_mat("Mat_LEDOrange", color=(1.0, 0.45, 0.0, 1.0), emission=(1.0, 0.45, 0.0, 1.0), emission_strength=10.0)

    # Mesh Helpers
    def add_cube(name, loc, scale, mat):
        bpy.ops.mesh.primitive_cube_add(location=loc)
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = scale
        obj.data.materials.append(mat)
        coll.objects.link(obj)
        bpy.context.collection.objects.unlink(obj)
        return obj

    def add_cyl(name, loc, rad, depth, rot=(0,0,0), mat=None):
        bpy.ops.mesh.primitive_cylinder_add(radius=rad, depth=depth, location=loc, rotation=rot)
        obj = bpy.context.active_object
        obj.name = name
        if mat: obj.data.materials.append(mat)
        coll.objects.link(obj)
        bpy.context.collection.objects.unlink(obj)
        return obj

    # --- 1. VERTICAL BLISTER CARD & TARGET PILL ---
    # Standing Vertical Foil Sheet at Y=0
    foil_sheet = add_cube("Vertical_Foil_Sheet", (0, 0, 0), (0.12, 0.001, 0.14), mat_foil)

    # Scored Vertical U-Flap (Hinged at top horizontal line)
    flap = add_cube("Vertical_Scored_U_Flap", (0, -0.001, -0.015), (0.015, 0.001, 0.018), mat_foil)

    # Target Capsule Pill (Positioned in front at Y = -0.015)
    pill_top = add_cyl("Target_Pill_Top", (0, -0.015, 0.006), 0.006, 0.012, (0,0,0), mat_pill_blue)
    pill_bot = add_cyl("Target_Pill_Bot", (0, -0.015, -0.006), 0.006, 0.012, (0,0,0), mat_pill_white)

    # Front PVC Bubble
    add_cube("PVC_Bubble_Front", (0, -0.02, 0), (0.012, 0.008, 0.02), mat_pvc)

    # --- 2. VERTICAL CNC GANTRY & TOOLHEAD (BEHIND FOIL AT +Y) ---
    add_cyl("Vertical_Guide_Rail_Z1", (0.08, 0.04, 0), 0.004, 0.24, (0,0,0), mat_aluminum)
    add_cyl("Vertical_Guide_Rail_Z2", (-0.08, 0.04, 0), 0.004, 0.24, (0,0,0), mat_aluminum)

    # Toolhead Carriage Block (Positioned behind vertical foil at +Y = 0.035)
    carriage = add_cube("Vertical_Carriage", (0, 0.035, 0), (0.02, 0.015, 0.028), mat_dark_metal)

    # Motorized Rotary Cutter Wheel
    cutter_wheel = add_cyl("Rotary_Cutter_Wheel", (0.016, 0.018, 0.012), 0.014, 0.002, (0, math.radians(90), 0), mat_cutter_steel)
    cutter_wheel.parent = carriage

    # Horizontal Silicone Plunger Pin (Extends in -Y direction through foil flap toward front bubble)
    plunger_body = add_cyl("Plunger_Body", (-0.014, 0.025, -0.005), 0.006, 0.024, (math.radians(90), 0, 0), mat_aluminum)
    plunger_body.parent = carriage

    plunger_pin = add_cyl("Plunger_Silicone_Pin", (-0.014, 0.012, -0.005), 0.004, 0.015, (math.radians(90), 0, 0), mat_silicone)
    plunger_pin.parent = carriage

    # LED Strip
    add_cube("Toolhead_LED", (0, 0.045, 0.018), (0.015, 0.002, 0.003), mat_led_orange)

    # Slanted Chute below vertical strip
    chute = add_cube("Delivery_Chute", (0, -0.04, -0.08), (0.08, 0.05, 0.008), mat_dark_metal)
    chute.rotation_euler = (math.radians(28), 0, 0)

    # --- 3. ANIMATION KEYFRAMING ---
    carriage.location = (-0.025, 0.035, 0.025)
    carriage.keyframe_insert(data_path="location", frame=1)

    carriage.location = (-0.016, 0.035, 0.02)
    carriage.keyframe_insert(data_path="location", frame=25)

    # Frame 35: Lower blade forward onto vertical foil
    carriage.location = (-0.016, 0.018, 0.02)
    carriage.keyframe_insert(data_path="location", frame=35)

    # Frame 50: Scoring Leg 1 (Downward vertical cut)
    carriage.location = (-0.016, 0.018, -0.02)
    carriage.keyframe_insert(data_path="location", frame=50)

    # Frame 65: Scoring Leg 2 (Horizontal bottom cut)
    carriage.location = (0.016, 0.018, -0.02)
    carriage.keyframe_insert(data_path="location", frame=65)

    # Frame 80: Scoring Leg 3 (Upward vertical cut)
    carriage.location = (0.016, 0.018, 0.02)
    carriage.keyframe_insert(data_path="location", frame=80)

    # Frame 85: Disengage blade (Retract +Y)
    carriage.location = (0.016, 0.035, 0.02)
    carriage.keyframe_insert(data_path="location", frame=85)

    # Frame 95: Align plunger over pill center
    carriage.location = (0.014, 0.035, 0.005)
    carriage.keyframe_insert(data_path="location", frame=95)

    carriage.location = (0.014, 0.035, 0.005)
    carriage.keyframe_insert(data_path="location", frame=105)

    carriage.location = (0.0, 0.035, 0.0)
    carriage.keyframe_insert(data_path="location", frame=120)

    # Plunger Pin Stroke (-Y direction)
    plunger_pin.location = (-0.014, 0.012, -0.005)
    plunger_pin.keyframe_insert(data_path="location", frame=95)

    plunger_pin.location = (-0.014, -0.008, -0.005) # Extends forward through flap
    plunger_pin.keyframe_insert(data_path="location", frame=105)

    plunger_pin.location = (-0.014, 0.012, -0.005)
    plunger_pin.keyframe_insert(data_path="location", frame=115)

    # Foil Flap Animation (Hinges forward around X-axis)
    flap.rotation_euler = (0, 0, 0)
    flap.keyframe_insert(data_path="rotation_euler", frame=80)

    flap.rotation_euler = (math.radians(-75), 0, 0) # Peels open -75 degrees
    flap.keyframe_insert(data_path="rotation_euler", frame=105)

    # Target Pill Ejection Animation (Pushed -Y and drops down -Z)
    pill_top.location = (0, -0.015, 0.006)
    pill_top.keyframe_insert(data_path="location", frame=100)
    pill_bot.location = (0, -0.015, -0.006)
    pill_bot.keyframe_insert(data_path="location", frame=100)

    pill_top.location = (0, -0.045, -0.065)
    pill_top.keyframe_insert(data_path="location", frame=118)
    pill_bot.location = (0, -0.045, -0.077)
    pill_bot.keyframe_insert(data_path="location", frame=118)

    # --- 4. LIGHTING & CAMERA SETUP ---
    target_empty = bpy.data.objects.new("Target_Center", None)
    target_empty.location = (0, 0, 0)
    coll.objects.link(target_empty)

    key_light = bpy.data.lights.new(name="Vert_Key", type='AREA')
    key_light.energy = 450.0
    key_light.size = 1.0
    key_light_obj = bpy.data.objects.new("Vert_Key", key_light)
    key_light_obj.location = (0.4, -0.6, 0.5)
    key_light_obj.rotation_euler = (math.radians(50), math.radians(10), math.radians(25))
    coll.objects.link(key_light_obj)

    fill_light = bpy.data.lights.new(name="Vert_Fill", type='AREA')
    fill_light.energy = 220.0
    fill_light.size = 1.2
    fill_light_obj = bpy.data.objects.new("Vert_Fill", fill_light)
    fill_light_obj.location = (-0.4, -0.5, 0.4)
    fill_light_obj.rotation_euler = (math.radians(45), math.radians(-15), math.radians(-35))
    coll.objects.link(fill_light_obj)

    cam_data = bpy.data.cameras.new("Cam_Vertical")
    cam_obj = bpy.data.objects.new("Cam_Vertical", cam_data)
    cam_obj.location = (0.35, -0.55, 0.28)
    coll.objects.link(cam_obj)
    
    tt = cam_obj.constraints.new(type='TRACK_TO')
    tt.target = target_empty
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'
    
    scene.camera = cam_obj

    blend_path = os.path.join(base_dir, "vertical_scoring_mechanism.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved vertical 3D Blender model file: {blend_path}")

    # Render Still Previews
    stills = {
        "vertical_strip_toolhead.png": 25,
        "vertical_u_flap.png": 80,
        "vertical_plunger_eject.png": 105
    }
    for fname, fnum in stills.items():
        scene.frame_set(fnum)
        scene.render.filepath = os.path.join(base_dir, fname)
        print(f"Rendering vertical still frame {fnum} -> {fname}...")
        bpy.ops.render.render(write_still=True)

    # Render 120 Animation Frames (PNG)
    scene.render.image_settings.file_format = 'PNG'
    scene.render.resolution_x = 854
    scene.render.resolution_y = 480
    if hasattr(scene, 'eevee') and hasattr(scene.eevee, 'taa_render_samples'):
        scene.eevee.taa_render_samples = 4

    for f in range(1, 121):
        scene.frame_set(f)
        frame_file = os.path.join(vert_frames_dir, f"frame_{f:04d}.png")
        scene.render.filepath = frame_file
        if f % 20 == 0 or f == 1 or f == 120:
            print(f"Rendering vertical frame {f}/120...")
        bpy.ops.render.render(write_still=True)

    print("=== Finished Blender 3D Frame Rendering ===")

if __name__ == "__main__":
    create_vertical_animation()
