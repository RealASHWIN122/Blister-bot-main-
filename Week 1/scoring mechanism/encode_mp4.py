import cv2
import glob
import os

def encode_frames_to_mp4():
    base_dir = r"c:\FARIS\Blister Bot\Blister-bot-main-\Week 1\scoring mechanism"
    anim_frames_dir = os.path.join(base_dir, "anim_frames")
    video_output_path = os.path.join(base_dir, "scoring_mechanism_demo.mp4")

    print("=== Encoding PNG Animation Frames to MP4 Video ===")
    frame_files = sorted(glob.glob(os.path.join(anim_frames_dir, "frame_*.png")))
    if not frame_files:
        print("Error: No rendered frames found in anim_frames directory!")
        return

    first_frame = cv2.imread(frame_files[0])
    height, width, _ = first_frame.shape
    fps = 24

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_output_path, fourcc, fps, (width, height))

    for idx, ff in enumerate(frame_files):
        img = cv2.imread(ff)
        out.write(img)
        if (idx + 1) % 30 == 0:
            print(f"Encoded frame {idx+1}/{len(frame_files)}...")

    out.release()
    print(f"=== Successfully Created MP4 Video: {video_output_path} ===")
    print(f"Video File Size: {os.path.getsize(video_output_path)} bytes")

if __name__ == "__main__":
    encode_frames_to_mp4()
