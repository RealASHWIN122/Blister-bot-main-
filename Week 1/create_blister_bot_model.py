import bpy
import math
import os

def create_blister_bot():
    print("=== Starting Blister Bot 3D Model Generation in Blender 5.2 ===")

    bpy.ops.wm.read_factory_settings(use_empty=True)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    render_dir = os.path.join(base_dir, "renders")
    os.makedirs(render_dir, exist_ok=True)

    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0

    bot_coll = bpy.data.collections.new("BlisterBot_Collection")
    scene.collection.children.link(bot_coll)

    # 2. Material Helper
    def create_material(name, color=(0.8, 0.8, 0.8, 1.0), metallic=0.0, roughness=0.5, transmission=0.0, alpha=1.0, emission=(0,0,0,1), emission_strength=0.0, is_glass=False):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        
        node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        node_bsdf.location = (0, 0)
        
        if 'Base Color' in node_bsdf.inputs:
            node_bsdf.inputs['Base Color'].default_value = color
        if 'Metallic' in node_bsdf.inputs:
            node_bsdf.inputs['Metallic'].default_value = metallic
        if 'Roughness' in node_bsdf.inputs:
            node_bsdf.inputs['Roughness'].default_value = roughness
        if 'Transmission Weight' in node_bsdf.inputs:
            node_bsdf.inputs['Transmission Weight'].default_value = transmission
        elif 'Transmission' in node_bsdf.inputs:
            node_bsdf.inputs['Transmission'].default_value = transmission
            
        if 'Alpha' in node_bsdf.inputs:
            node_bsdf.inputs['Alpha'].default_value = alpha
            
        if 'Emission Color' in node_bsdf.inputs:
            node_bsdf.inputs['Emission Color'].default_value = emission
        elif 'Emission' in node_bsdf.inputs:
            node_bsdf.inputs['Emission'].default_value = emission
            
        if 'Emission Strength' in node_bsdf.inputs:
            node_bsdf.inputs['Emission Strength'].default_value = emission_strength
            
        node_output = nodes.new(type='ShaderNodeOutputMaterial')
        node_output.location = (300, 0)
        
        mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])

        if is_glass:
            if hasattr(mat, 'blend_method'):
                try:
                    mat.blend_method = 'BLEND'
                except Exception:
                    pass
            if hasattr(mat, 'shadow_method'):
                try:
                    mat.shadow_method = 'NONE'
                except Exception:
                    pass

        return mat

    # Materials
    mat_white_plastic = create_material("Mat_White_Plastic", color=(0.94, 0.95, 0.96, 1.0), roughness=0.25)
    mat_dark_casing = create_material("Mat_Dark_Casing", color=(0.12, 0.13, 0.15, 1.0), roughness=0.3)
    mat_metal_aluminum = create_material("Mat_Metal_Aluminum", color=(0.85, 0.86, 0.88, 1.0), metallic=0.95, roughness=0.15)
    mat_metal_dark = create_material("Mat_Metal_Dark", color=(0.25, 0.26, 0.28, 1.0), metallic=0.9, roughness=0.25)
    mat_glass_acrylic = create_material("Mat_Glass_Acrylic", color=(0.85, 0.95, 1.0, 1.0), roughness=0.01, transmission=0.95, alpha=0.15, is_glass=True)
    
    mat_screen_bg = create_material("Mat_Screen_BG", color=(0.02, 0.05, 0.12, 1.0), emission=(0.02, 0.05, 0.12, 1.0), emission_strength=1.5)
    mat_screen_ui_green = create_material("Mat_Screen_UI_Green", color=(0.1, 0.85, 0.45, 1.0), emission=(0.1, 0.85, 0.45, 1.0), emission_strength=4.0)
    mat_screen_ui_blue = create_material("Mat_Screen_UI_Blue", color=(0.0, 0.65, 1.0, 1.0), emission=(0.0, 0.65, 1.0, 1.0), emission_strength=3.0)
    mat_led_cyan = create_material("Mat_LED_Cyan", color=(0.0, 0.85, 1.0, 1.0), emission=(0.0, 0.85, 1.0, 1.0), emission_strength=8.0)
    mat_led_warm = create_material("Mat_LED_Warm", color=(1.0, 0.92, 0.75, 1.0), emission=(1.0, 0.92, 0.75, 1.0), emission_strength=6.0)
    
    mat_stepper_body = create_material("Mat_Stepper_Body", color=(0.14, 0.14, 0.16, 1.0), metallic=0.7, roughness=0.3)
    mat_pill_blue = create_material("Mat_Pill_Blue", color=(0.0, 0.45, 0.95, 1.0), roughness=0.1)
    mat_pill_white = create_material("Mat_Pill_White", color=(0.98, 0.98, 0.98, 1.0), roughness=0.1)
    mat_blister_foil = create_material("Mat_Blister_Foil", color=(0.9, 0.91, 0.93, 1.0), metallic=0.98, roughness=0.12)
    mat_blister_pvc = create_material("Mat_Blister_PVC", color=(0.9, 0.95, 1.0, 1.0), roughness=0.05, transmission=0.85, alpha=0.3, is_glass=True)
    mat_plunger_silicone = create_material("Mat_Plunger_Silicone", color=(0.95, 0.35, 0.1, 1.0), roughness=0.4)

    # Mesh Helpers
    def add_cube(name, location, scale, material, parent=None):
        bpy.ops.mesh.primitive_cube_add(location=location)
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = scale
        obj.data.materials.append(material)
        bot_coll.objects.link(obj)
        bpy.context.collection.objects.unlink(obj)
        if parent:
            obj.parent = parent
        return obj

    def add_cylinder(name, location, radius, depth, rotation=(0,0,0), material=None, parent=None):
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location, rotation=rotation)
        obj = bpy.context.active_object
        obj.name = name
        if material:
            obj.data.materials.append(material)
        bot_coll.objects.link(obj)
        bpy.context.collection.objects.unlink(obj)
        if parent:
            obj.parent = parent
        return obj

    # Root Target Empty
    root = bpy.data.objects.new("BlisterBot_Root", None)
    root.location = (0, 0, 0)
    bot_coll.objects.link(root)

    target_center = bpy.data.objects.new("Target_Center", None)
    target_center.location = (0, -0.02, 0.16)
    bot_coll.objects.link(target_center)

    target_mech = bpy.data.objects.new("Target_Mech", None)
    target_mech.location = (-0.085, -0.01, 0.16)
    bot_coll.objects.link(target_mech)

    # --- A. HOLLOW CHASSIS STRUCTURE ---
    # 1. Solid Right Casing (Houses Screen & Electronics)
    right_box = add_cube("Right_Chassis_Box", (0.095, 0, 0.16), (0.095, 0.14, 0.16), mat_white_plastic, root)
    bev_r = right_box.modifiers.new(name="Bevel", type='BEVEL')
    bev_r.width = 0.02
    bev_r.segments = 4

    # 2. Left Chamber Enclosure Walls (Top, Bottom, Left, Back)
    top_roof = add_cube("Chamber_Roof", (-0.095, 0, 0.315), (0.095, 0.14, 0.005), mat_white_plastic, root)
    bot_floor = add_cube("Chamber_Floor", (-0.095, 0, 0.005), (0.095, 0.14, 0.005), mat_white_plastic, root)
    left_wall = add_cube("Chamber_LeftWall", (-0.185, 0, 0.16), (0.005, 0.14, 0.15), mat_white_plastic, root)
    back_wall = add_cube("Chamber_Backwall", (-0.095, 0.135, 0.16), (0.095, 0.005, 0.15), mat_dark_casing, root)

    # Internal Lighting Strips
    add_cube("Chamber_Top_LED", (-0.095, -0.02, 0.308), (0.085, 0.11, 0.004), mat_led_warm, root)
    add_cube("Chamber_Side_LED", (-0.180, -0.02, 0.16), (0.003, 0.11, 0.12), mat_led_cyan, root)

    # Front Acrylic Door (Left Chamber Front Window)
    acrylic_door = add_cube("Acrylic_Window_Door", (-0.095, -0.138, 0.16), (0.088, 0.002, 0.148), mat_glass_acrylic, root)
    door_handle = add_cube("Door_Handle_Metal", (-0.095, -0.142, 0.038), (0.045, 0.005, 0.008), mat_metal_aluminum, root)

    # --- B. FRONT RIGHT CONTROL PANEL ---
    # Display UI Screen
    add_cube("Screen_Bezel", (0.095, -0.141, 0.175), (0.062, 0.002, 0.082), mat_dark_casing, root)
    add_cube("Screen_Background", (0.095, -0.143, 0.175), (0.058, 0.001, 0.078), mat_screen_bg, root)

    # Screen UI Widgets
    add_cube("UI_Header_Bar", (0.095, -0.144, 0.235), (0.052, 0.0005, 0.008), mat_screen_ui_blue, root)
    add_cube("UI_Blister_Card", (0.095, -0.144, 0.175), (0.045, 0.0005, 0.04), mat_metal_dark, root)
    add_cube("UI_Action_Btn", (0.095, -0.144, 0.115), (0.04, 0.0005, 0.008), mat_screen_ui_green, root)

    # Camera Module
    add_cube("Camera_Housing", (0.095, -0.142, 0.282), (0.024, 0.008, 0.016), mat_dark_casing, root)
    add_cylinder("Camera_Ring", (0.095, -0.151, 0.282), 0.01, 0.004, (math.radians(90), 0, 0), mat_metal_dark, root)
    add_cylinder("Camera_Lens", (0.095, -0.154, 0.282), 0.005, 0.002, (math.radians(90), 0, 0), mat_led_cyan, root)

    # Status LED Strip
    add_cube("LED_Status_Strip", (0.095, -0.142, 0.075), (0.048, 0.003, 0.004), mat_led_cyan, root)

    # Dispensing Drawer
    add_cube("Dispensing_Drawer", (0.095, -0.139, 0.038), (0.06, 0.004, 0.022), mat_white_plastic, root)
    add_cube("Drawer_Handle", (0.095, -0.144, 0.038), (0.026, 0.004, 0.005), mat_metal_aluminum, root)

    # --- C. INTERNAL MECHANICS (IN HOLLOW LEFT CAVITY) ---
    rack_base = add_cube("Rack_Support_Structure", (-0.095, 0.02, 0.16), (0.075, 0.06, 0.11), mat_metal_dark, root)

    # 4 loaded blister pack strips
    blister_xs = [-0.14, -0.11, -0.08, -0.05]
    for idx, bx in enumerate(blister_xs):
        add_cube(f"Blister_Foil_{idx}", (bx, -0.01, 0.16), (0.011, 0.001, 0.095), mat_blister_foil, root)

        for r in range(5):
            for c in range(2):
                py = -0.005 + c * 0.014
                pz = 0.085 + r * 0.036
                
                add_cube(f"Bubble_{idx}_{r}_{c}", (bx, py - 0.004, pz), (0.006, 0.005, 0.011), mat_blister_pvc, root)
                add_cylinder(f"Capsule_Top_{idx}_{r}_{c}", (bx, py - 0.004, pz + 0.004), 0.004, 0.007, (0,0,0), mat_pill_blue, root)
                add_cylinder(f"Capsule_Bot_{idx}_{r}_{c}", (bx, py - 0.004, pz - 0.004), 0.004, 0.007, (0,0,0), mat_pill_white, root)

    # 2-Axis CNC Stepper Gantry
    add_cube("Gantry_X_Rail_Top", (-0.095, -0.065, 0.27), (0.082, 0.008, 0.008), mat_metal_aluminum, root)
    add_cube("Gantry_X_Rail_Bottom", (-0.095, -0.065, 0.05), (0.082, 0.008, 0.008), mat_metal_aluminum, root)

    add_cylinder("Gantry_LeadScrew", (-0.08, -0.065, 0.16), 0.004, 0.22, (0,0,0), mat_metal_aluminum, root)
    add_cylinder("Gantry_GuideRod", (-0.11, -0.065, 0.16), 0.004, 0.22, (0,0,0), mat_metal_aluminum, root)

    def add_nema17(name, location):
        m1 = add_cube(f"{name}_Body", location, (0.021, 0.021, 0.021), mat_stepper_body, root)
        m2 = add_cube(f"{name}_Plate", (location[0], location[1]-0.022, location[2]), (0.021, 0.002, 0.021), mat_metal_aluminum, root)
        m3 = add_cylinder(f"{name}_Shaft", (location[0], location[1]-0.03, location[2]), 0.0025, 0.015, (math.radians(90),0,0), mat_metal_aluminum, root)
        return m1

    add_nema17("Motor_X", (-0.165, -0.065, 0.27))
    add_nema17("Motor_Y", (-0.08, -0.065, 0.025))

    add_cube("Toolhead_Carriage", (-0.085, -0.055, 0.16), (0.018, 0.014, 0.024), mat_metal_dark, root)

    add_cylinder("Rotary_Cutter_Wheel", (-0.085, -0.035, 0.17), 0.014, 0.002, (0, math.radians(90), 0), mat_metal_dark, root)
    add_cylinder("Plunger_Body", (-0.085, -0.038, 0.145), 0.006, 0.024, (0,0,0), mat_metal_aluminum, root)
    add_cylinder("Plunger_Tip", (-0.085, -0.026, 0.145), 0.004, 0.01, (math.radians(90), 0, 0), mat_plunger_silicone, root)

    chute = add_cube("Delivery_Chute", (-0.095, -0.06, 0.022), (0.07, 0.05, 0.008), mat_dark_casing, root)
    chute.rotation_euler = (math.radians(22), 0, 0)

    # Studio Floor
    add_cube("Studio_Floor_Table", (0, 0, -0.005), (0.9, 0.7, 0.005), mat_dark_casing, None)

    # --- D. LIGHTING ---
    key_light_data = bpy.data.lights.new(name="Key_Light", type='AREA')
    key_light_data.energy = 400.0
    key_light_data.size = 1.5
    key_light_obj = bpy.data.objects.new("Key_Light", key_light_data)
    key_light_obj.location = (0.7, -0.9, 0.8)
    key_light_obj.rotation_euler = (math.radians(52), math.radians(12), math.radians(35))
    bot_coll.objects.link(key_light_obj)

    fill_light_data = bpy.data.lights.new(name="Fill_Light", type='AREA')
    fill_light_data.energy = 200.0
    fill_light_data.size = 1.5
    fill_light_obj = bpy.data.objects.new("Fill_Light", fill_light_data)
    fill_light_obj.location = (-0.7, -0.8, 0.6)
    fill_light_obj.rotation_euler = (math.radians(48), math.radians(-18), math.radians(-38))
    bot_coll.objects.link(fill_light_obj)

    rim_light_data = bpy.data.lights.new(name="Rim_Light", type='SPOT')
    rim_light_data.energy = 400.0
    rim_light_obj = bpy.data.objects.new("Rim_Light", rim_light_data)
    rim_light_obj.location = (0.0, 0.9, 0.7)
    rim_light_obj.rotation_euler = (math.radians(-50), 0, 0)
    bot_coll.objects.link(rim_light_obj)

    # --- E. CAMERAS SETUP ---
    cameras = {}

    def setup_camera(name, location, target_obj):
        cam_data = bpy.data.cameras.new(name)
        cam_obj = bpy.data.objects.new(name, cam_data)
        cam_obj.location = location
        bot_coll.objects.link(cam_obj)
        
        tt = cam_obj.constraints.new(type='TRACK_TO')
        tt.target = target_obj
        tt.track_axis = 'TRACK_NEGATIVE_Z'
        tt.up_axis = 'UP_Y'
        return cam_obj

    cam1 = setup_camera("Cam_Perspective", (0.58, -0.78, 0.42), target_center)
    cameras["render_perspective.png"] = (cam1, False)

    cam2 = setup_camera("Cam_Mechanism", (-0.095, -0.45, 0.16), target_mech)
    cameras["render_mechanism.png"] = (cam2, True)

    cam3 = setup_camera("Cam_Front", (0.0, -0.85, 0.16), target_center)
    cameras["render_front.png"] = (cam3, False)

    # Save Native Blender File
    blend_path = os.path.join(base_dir, "blister_bot.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved native Blender model file to: {blend_path}")

    # Render Preview Images
    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        try:
            scene.render.engine = 'BLENDER_EEVEE'
        except Exception:
            scene.render.engine = 'CYCLES'
            
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100

    for fname, (cam_obj, hide_win) in cameras.items():
        scene.camera = cam_obj
        acrylic_door.hide_render = hide_win
        door_handle.hide_render = hide_win
        
        out_filepath = os.path.join(render_dir, fname)
        scene.render.filepath = out_filepath
        print(f"Rendering view: {fname}...")
        bpy.ops.render.render(write_still=True)
        print(f"Successfully rendered: {out_filepath}")

    print("=== Finished Blister Bot 3D Model Generation Successfully ===")

if __name__ == "__main__":
    create_blister_bot()
