import cv2
import glob
import os

def encode_vertical_mp4():
    base_dir = r"c:\FARIS\Blister Bot\Blister-bot-main-\Week 1\vertical scoring mechanism"
    vert_frames_dir = os.path.join(base_dir, "vert_frames")
    video_out = os.path.join(base_dir, "vertical_strip_ejection_demo.mp4")

    print("=== Encoding Vertical PNG Frames into MP4 Video ===")
    frame_files = sorted(glob.glob(os.path.join(vert_frames_dir, "frame_*.png")))
    if not frame_files:
        print("Error: No rendered vertical frames found!")
        return

    first_frame = cv2.imread(frame_files[0])
    height, width, _ = first_frame.shape
    fps = 24

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_out, fourcc, fps, (width, height))

    for idx, ff in enumerate(frame_files):
        img = cv2.imread(ff)
        out.write(img)
        if (idx + 1) % 30 == 0:
            print(f"Encoded vertical frame {idx+1}/{len(frame_files)}...")

    out.release()
    print(f"=== Successfully Generated Vertical Strip MP4 Video: {video_out} ===")
    print(f"Video File Size: {os.path.getsize(video_out)} bytes")

if __name__ == "__main__":
    encode_vertical_mp4()
