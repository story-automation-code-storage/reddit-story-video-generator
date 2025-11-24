import os
import subprocess
import random


def get_ffmpeg_path():
    ffmpeg = os.getenv("FFMPEG_PATH", "")
    return ffmpeg.strip() or "ffmpeg"


def render_background(schedule, output_path):
    if not schedule:
        raise RuntimeError("Schedule empty.")

    ffmpeg = get_ffmpeg_path()

    input_args = []
    filter_parts = []
    concat_nodes = []

    for idx, seg in enumerate(schedule):

        input_args += [
            "-ss", str(seg["in"]),
            "-t", str(seg["duration"]),
            "-i", seg["clip"],
        ]

        filter_parts.append(
            f"[{idx}:v]"
            f"scale=1080:-1:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,"
            f"setsar=1[v{idx}]"
        )

        concat_nodes.append(f"[v{idx}]")

    filter_complex = ";".join(filter_parts)
    concat_filter = f"{''.join(concat_nodes)}concat=n={len(schedule)}:v=1[outv]"
    full_filter = f"{filter_complex};{concat_filter}"

    cmd = [
        ffmpeg,
        "-y",
        *input_args,
        "-filter_complex", full_filter,
        "-map", "[outv]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        output_path,
    ]

    print("FFmpeg command:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print("Background rendered:", output_path)
