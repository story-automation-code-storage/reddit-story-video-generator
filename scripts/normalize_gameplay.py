import os
import subprocess

INPUT_DIR = "assets/gameplay"
OUTPUT_DIR = "assets/gameplay_normalized"

def normalize_clip(filename):
    input_path = os.path.join(INPUT_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, filename)

    # Skip files that disappeared or are not real video
    if not os.path.isfile(input_path):
        print(f"Skipping missing or phantom file: {filename}")
        return

    print("Normalizing:", filename)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf", "scale=1080:-1,crop=1080:1920:0:(in_h-1920)/2",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-an",
        output_path
    ]

    subprocess.run(cmd, check=False)  # avoid stopping entire batch


def run():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".mp4")]

    for f in files:
        normalize_clip(f)

    print("DONE — all valid files processed.")


if __name__ == "__main__":
    run()
