import bpy
import math
import os

def create_and_animate_scoring_mechanism():
    print("=== Starting 3D Kinematic Animation of Deblistering Scoring Mechanism in Blender 5.2 ===")

    # Reset scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    base_dir = r"c:\FARIS\Blister Bot\Blister-bot-main-\Week 1\scoring mechanism"
    os.makedirs(base_dir, exist_ok=True)

    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.frame_start = 1
    scene.frame_end = 120
    scene.render.fps = 24

    coll = bpy.data.collections.new("ScoringMechanism_Collection")
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
    mat_aluminum = create_mat("Mat_Aluminum", color=(0.8, 0.82, 0.85, 1.0), metallic=0.95, roughness=0.2)
    mat_dark_metal = create_mat("Mat_DarkMetal", color=(0.2, 0.22, 0.25, 1.0), metallic=0.9, roughness=0.25)
    mat_pill_blue = create_mat("Mat_PillBlue", color=(0.0, 0.45, 0.95, 1.0), roughness=0.1)
    mat_pill_white = create_mat("Mat_PillWhite", color=(0.98, 0.98, 0.98, 1.0), roughness=0.1)
    mat_silicone = create_mat("Mat_Silicone", color=(0.95, 0.35, 0.1, 1.0), roughness=0.4)
    mat_cutter_steel = create_mat("Mat_CutterSteel", color=(0.3, 0.32, 0.35, 1.0), metallic=0.95, roughness=0.1)
    mat_led_cyan = create_mat("Mat_LEDCyan", color=(0.0, 0.85, 1.0, 1.0), emission=(0.0, 0.85, 1.0, 1.0), emission_strength=10.0)

    # Mesh Builders
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

    # --- 1. BLISTER PACK SHEET & TARGET PILL ---
    # Main Aluminum Foil Backing Sheet
    foil_card = add_cube("Foil_Sheet", (0, 0, 0), (0.12, 0.001, 0.14), mat_foil)

    # Scored U-Flap (Hinged aluminum flap over target pill center)
    flap = add_cube("Scored_U_Flap", (0, -0.0015, 0), (0.015, 0.001, 0.018), mat_foil)

    # Target Capsule Pill (Pill center at (0, 0.01, 0))
    pill_top = add_cyl("Target_Pill_Top", (0, 0.012, 0.006), 0.006, 0.012, (0,0,0), mat_pill_blue)
    pill_bot = add_cyl("Target_Pill_Bot", (0, 0.012, -0.006), 0.006, 0.012, (0,0,0), mat_pill_white)

    # Translucent PVC Bubble Pocket on front
    add_cube("PVC_Bubble_Front", (0, 0.018, 0), (0.012, 0.008, 0.02), mat_pvc)

    # --- 2. 2-AXIS CNC GANTRY & TOOLHEAD ASSEMBLY ---
    # CNC Linear Rails & Lead Screw
    add_cube("Rail_X_Top", (0, -0.04, 0.10), (0.15, 0.008, 0.008), mat_aluminum)
    add_cube("Rail_X_Bottom", (0, -0.04, -0.10), (0.15, 0.008, 0.008), mat_aluminum)
    add_cyl("Lead_Screw_Y", (0.05, -0.04, 0), 0.004, 0.22, (0,0,0), mat_aluminum)

    # Toolhead Carriage Block (Root object for motion animation)
    carriage = add_cube("Toolhead_Carriage", (0, -0.035, 0), (0.02, 0.015, 0.028), mat_dark_metal)

    # Motorized Rotary Cutter Wheel (Child of carriage)
    cutter_wheel = add_cyl("Rotary_Cutter_Wheel", (0.016, -0.018, 0.012), 0.014, 0.002, (0, math.radians(90), 0), mat_cutter_steel)
    cutter_wheel.parent = carriage

    # Soft Silicone Plunger Assembly (Child of carriage)
    plunger_body = add_cyl("Plunger_Body", (-0.014, -0.025, -0.005), 0.006, 0.024, (math.radians(90), 0, 0), mat_aluminum)
    plunger_body.parent = carriage

    plunger_pin = add_cyl("Plunger_Silicone_Pin", (-0.014, -0.012, -0.005), 0.004, 0.015, (math.radians(90), 0, 0), mat_silicone)
    plunger_pin.parent = carriage

    # LED Accent
    add_cube("Toolhead_LED", (0, -0.045, 0.018), (0.015, 0.002, 0.003), mat_led_cyan)

    # Delivery Chute
    chute = add_cube("Delivery_Chute", (0, -0.04, -0.08), (0.08, 0.05, 0.008), mat_dark_metal)
    chute.rotation_euler = (math.radians(25), 0, 0)

    # --- 3. ANIMATION KEYFRAMING (120 FRAMES) ---
    # A. Carriage Motion (X, Z trajectory for 270-degree U-scoring)
    # Frame 1: Approach home position
    carriage.location = (-0.025, -0.035, 0.025)
    carriage.keyframe_insert(data_path="location", frame=1)

    # Frame 25: Positioning cutter wheel at Top-Left corner (P1)
    carriage.location = (-0.016, -0.035, 0.02)
    carriage.keyframe_insert(data_path="location", frame=25)

    # Frame 35: Lowering cutter wheel onto foil backing (Y depth engage)
    carriage.location = (-0.016, -0.018, 0.02)
    carriage.keyframe_insert(data_path="location", frame=35)

    # Frame 50: Scoring Leg 1 (Downward left cut to P2)
    carriage.location = (-0.016, -0.018, -0.02)
    carriage.keyframe_insert(data_path="location", frame=50)

    # Frame 65: Scoring Leg 2 (Horizontal bottom cut P2 -> P3)
    carriage.location = (0.016, -0.018, -0.02)
    carriage.keyframe_insert(data_path="location", frame=65)

    # Frame 80: Scoring Leg 3 (Upward right cut P3 -> P4)
    carriage.location = (0.016, -0.018, 0.02)
    carriage.keyframe_insert(data_path="location", frame=80)

    # Frame 85: Disengaging cutter wheel (retract Y)
    carriage.location = (0.016, -0.035, 0.02)
    carriage.keyframe_insert(data_path="location", frame=85)

    # Frame 95: Aligning silicone plunger pin over scored center (0, 0)
    carriage.location = (0.014, -0.035, 0.005)
    carriage.keyframe_insert(data_path="location", frame=95)

    # Frame 105: Plunger hold position
    carriage.location = (0.014, -0.035, 0.005)
    carriage.keyframe_insert(data_path="location", frame=105)

    # Frame 120: Return home
    carriage.location = (0.0, -0.035, 0.0)
    carriage.keyframe_insert(data_path="location", frame=120)

    # B. Plunger Extension Pin Animation (Pin moves forward in Y)
    plunger_pin.location = (-0.014, -0.012, -0.005)
    plunger_pin.keyframe_insert(data_path="location", frame=95)

    # Frame 105: Plunger extends through foil flap to push pill
    plunger_pin.location = (-0.014, 0.008, -0.005)
    plunger_pin.keyframe_insert(data_path="location", frame=105)

    # Frame 115: Plunger retracts back
    plunger_pin.location = (-0.014, -0.012, -0.005)
    plunger_pin.keyframe_insert(data_path="location", frame=115)

    # C. Foil U-Flap Opening Animation (Hinges downward around X-axis)
    flap.rotation_euler = (0, 0, 0)
    flap.keyframe_insert(data_path="rotation_euler", frame=80)

    flap.rotation_euler = (math.radians(75), 0, 0) # Peels open 75 degrees!
    flap.keyframe_insert(data_path="rotation_euler", frame=105)

    # D. Target Capsule Pill Ejection Animation (Drops down Y and Z into chute)
    pill_top.location = (0, 0.012, 0.006)
    pill_top.keyframe_insert(data_path="location", frame=100)
    pill_bot.location = (0, 0.012, -0.006)
    pill_bot.keyframe_insert(data_path="location", frame=100)

    # Frame 118: Capsule pill ejected through flap and dropping down chute
    pill_top.location = (0, -0.035, -0.065)
    pill_top.keyframe_insert(data_path="location", frame=118)
    pill_bot.location = (0, -0.035, -0.077)
    pill_bot.keyframe_insert(data_path="location", frame=118)

    # --- 4. LIGHTING & CAMERA SETUP ---
    key_light = bpy.data.lights.new(name="Scoring_Key", type='AREA')
    key_light.energy = 400.0
    key_light.size = 0.8
    key_light_obj = bpy.data.objects.new("Scoring_Key", key_light)
    key_light_obj.location = (0.3, -0.5, 0.4)
    key_light_obj.rotation_euler = (math.radians(50), math.radians(10), math.radians(25))
    coll.objects.link(key_light_obj)

    fill_light = bpy.data.lights.new(name="Scoring_Fill", type='AREA')
    fill_light.energy = 180.0
    fill_light.size = 1.0
    fill_light_obj = bpy.data.objects.new("Scoring_Fill", fill_light)
    fill_light_obj.location = (-0.4, -0.4, 0.3)
    fill_light_obj.rotation_euler = (math.radians(45), math.radians(-15), math.radians(-35))
    coll.objects.link(fill_light_obj)

    cam_data = bpy.data.cameras.new("Cam_Scoring")
    cam_obj = bpy.data.objects.new("Cam_Scoring", cam_data)
    cam_obj.location = (0.18, -0.32, 0.12)
    cam_obj.rotation_euler = (math.radians(68), 0, math.radians(28))
    coll.objects.link(cam_obj)
    scene.camera = cam_obj

    # Save Blend File
    blend_path = os.path.join(base_dir, "scoring_mechanism.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved specialized Blender model file: {blend_path}")

    # Render Still Keyframe Previews
    stills = {
        "scoring_toolhead.png": 25,
        "u_flap_scored.png": 80,
        "tablet_ejection.png": 105
    }
    for fname, fnum in stills.items():
        scene.frame_set(fnum)
        scene.render.filepath = os.path.join(base_dir, fname)
        print(f"Rendering still keyframe frame {fnum} -> {fname}...")
        bpy.ops.render.render(write_still=True)

    # --- 5. RENDER MP4 ANIMATION VIDEO ---
    video_path = os.path.join(base_dir, "scoring_mechanism_demo.mp4")
    print(f"Configuring MP4 video rendering output to: {video_path}...")
    
    scene.render.filepath = video_path
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    scene.render.ffmpeg.ffmpeg_preset = 'GOOD'

    print("Rendering MP4 animation video sequence (Frames 1-120)...")
    bpy.ops.render.render(animation=True)
    print(f"=== Successfully Rendered Scoring Mechanism MP4 Video: {video_path} ===")

if __name__ == "__main__":
    create_and_animate_scoring_mechanism()
