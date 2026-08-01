import bpy
import os

def render_anim_frames():
    base_dir = r"c:\FARIS\Blister Bot\Blister-bot-main-\Week 1\scoring mechanism"
    anim_frames_dir = os.path.join(base_dir, "anim_frames")
    os.makedirs(anim_frames_dir, exist_ok=True)

    print("=== Rendering Fast 120 Animation Frames in Blender 5.2 ===")
    blend_file = os.path.join(base_dir, "scoring_mechanism.blend")
    
    bpy.ops.wm.open_mainfile(filepath=blend_file)
    scene = bpy.context.scene

    scene.render.image_settings.file_format = 'PNG'
    scene.render.resolution_x = 854
    scene.render.resolution_y = 480
    
    if hasattr(scene, 'eevee'):
        if hasattr(scene.eevee, 'taa_render_samples'):
            scene.eevee.taa_render_samples = 4

    for f in range(1, 121):
        scene.frame_set(f)
        frame_filename = os.path.join(anim_frames_dir, f"frame_{f:04d}.png")
        scene.render.filepath = frame_filename
        if f % 20 == 0 or f == 1 or f == 120:
            print(f"Rendering frame {f}/120...")
        bpy.ops.render.render(write_still=True)

    print("=== All 120 Animation Frames Rendered Successfully ===")

if __name__ == "__main__":
    render_anim_frames()
