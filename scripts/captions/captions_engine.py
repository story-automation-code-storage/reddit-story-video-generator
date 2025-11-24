"""
Captions Engine - Burn animated captions into video using FFmpeg.
"""

import os
import subprocess
from scripts.captions.srt_builder import generate_srt_file


def burn_captions_into_video(
    video_path: str,
    srt_path: str,
    output_path: str,
    font_size: int = 42,
    font_color: str = "white",
    border_color: str = "black",
    border_width: int = 3
):
    """
    Burn .srt subtitles into video using FFmpeg subtitles filter.

    Styling:
    - Bold white text
    - Black stroke/outline
    - Centered at bottom of screen

    Args:
        video_path: Input video file
        srt_path: Subtitle file (.srt)
        output_path: Output video with burned captions
        font_size: Caption font size (px)
        font_color: Caption text color
        border_color: Caption border/stroke color
        border_width: Border thickness
    """
    # Escape path for FFmpeg filter
    srt_escaped = srt_path.replace('\\', '/').replace(':', '\\\\:')

    # Build subtitles filter
    # FFmpeg subtitles filter with custom styling
    subtitles_filter = (
        f"subtitles={srt_escaped}:"
        f"force_style='FontSize={font_size},"
        f"PrimaryColour=&H00FFFFFF,"  # White text (ABGR format)
        f"OutlineColour=&H00000000,"  # Black outline
        f"BorderStyle=3,"  # Opaque box behind text
        f"Outline={border_width},"
        f"Shadow=0,"
        f"Alignment=2,"  # Bottom center
        f"MarginV=80'"  # Margin from bottom
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vf", subtitles_filter,
        "-codec:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-codec:a", "copy",
        output_path
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Captions burned into video: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"❌ Error burning captions: {e}")
        # Fallback: copy video without captions
        print("Falling back to video without captions...")
        subprocess.run(["ffmpeg", "-y", "-i", video_path, "-codec", "copy", output_path], check=True)
        return output_path


def apply_captions_to_video(
    video_path: str,
    story_text: str,
    audio_duration: float,
    output_folder: str = "output"
) -> str:
    """
    Main function: Generate captions and burn them into video.

    Process:
    1. Generate .srt file from story text
    2. Burn captions into video using FFmpeg

    Returns: path to captioned video
    """
    # Generate SRT file
    srt_path = os.path.join(output_folder, "captions_temp.srt")
    generate_srt_file(story_text, audio_duration, srt_path)

    # Burn captions into video
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    output_path = os.path.join(output_folder, f"{base_name}_CAPTIONED.mp4")

    return burn_captions_into_video(video_path, srt_path, output_path)
