"""
Background Music Engine - Automatically select and mix background music based on story tone.
"""

import os
import random
import subprocess
from pathlib import Path


def analyze_story_tone(story_text: str) -> str:
    """
    Analyze story and return emotional tone.
    Reuses the same logic as TTS voice selection for consistency.

    Returns: 'dark', 'fun', 'warm', or 'neutral'
    """
    s = story_text.lower()

    # Tone inference based on emotion keywords
    dark_cues = ["terrified", "panicked", "breaking down", "trauma", "stalking", "creepy", "dark", "anxiety", "horror", "scared"]
    fun_cues = ["funniest", "laughing", "joked", "ridiculous", "couldn't stop laughing", "hilarious", "funny", "comedy"]
    warm_cues = ["heartwarming", "kind", "gentle", "sweet", "wholesome", "grateful", "comforting", "touching", "emotional"]

    if any(k in s for k in dark_cues):
        return "dark"
    elif any(k in s for k in fun_cues):
        return "fun"
    elif any(k in s for k in warm_cues):
        return "warm"
    else:
        return "neutral"


def select_music_track(tone: str, music_folder: str = "assets/music") -> str:
    """
    Select a random music track based on the story tone.

    Expected folder structure:
        assets/music/
            dark/       - suspenseful tracks
            fun/        - upbeat tracks
            warm/       - mellow tracks
            neutral/    - chill background tracks

    Returns: path to selected music file
    """
    tone_folder = os.path.join(music_folder, tone)

    if not os.path.isdir(tone_folder):
        print(f"Warning: Music folder '{tone_folder}' not found. Trying neutral...")
        tone_folder = os.path.join(music_folder, "neutral")

    if not os.path.isdir(tone_folder):
        raise RuntimeError(f"No music folder found. Please add music files to {music_folder}/[dark|fun|warm|neutral]/")

    # Get all audio files
    music_files = [
        os.path.join(tone_folder, f)
        for f in os.listdir(tone_folder)
        if f.lower().endswith(('.mp3', '.wav', '.m4a', '.aac'))
    ]

    if not music_files:
        raise RuntimeError(f"No music files found in {tone_folder}")

    return random.choice(music_files)


def normalize_music_length(music_path: str, target_duration: float, output_path: str, fade_duration: float = 2.0):
    """
    Normalize music track to match target duration using FFmpeg.
    - If music is longer: trim and add fade out
    - If music is shorter: loop and add fade out

    Args:
        music_path: Input music file
        target_duration: Target duration in seconds
        output_path: Output file path
        fade_duration: Fade in/out duration in seconds
    """
    # Get music duration
    probe_cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        music_path
    ]
    result = subprocess.run(probe_cmd, capture_output=True, text=True)
    music_duration = float(result.stdout.strip())

    if music_duration >= target_duration:
        # Music is longer - just trim with fade
        cmd = [
            "ffmpeg",
            "-y",
            "-i", music_path,
            "-t", str(target_duration),
            "-af", f"afade=t=in:d={fade_duration},afade=t=out:st={target_duration - fade_duration}:d={fade_duration}",
            "-codec:a", "aac",
            "-b:a", "192k",
            output_path
        ]
    else:
        # Music is shorter - loop it
        loops_needed = int(target_duration / music_duration) + 1
        cmd = [
            "ffmpeg",
            "-y",
            "-stream_loop", str(loops_needed),
            "-i", music_path,
            "-t", str(target_duration),
            "-af", f"afade=t=in:d={fade_duration},afade=t=out:st={target_duration - fade_duration}:d={fade_duration}",
            "-codec:a", "aac",
            "-b:a", "192k",
            output_path
        ]

    subprocess.run(cmd, check=True)
    print(f"Music normalized: {output_path} ({target_duration}s)")


def duck_music_for_speech(music_path: str, narration_path: str, output_path: str, duck_level: float = 0.25):
    """
    Apply ducking effect: lower music volume when narration is present.
    This is a simplified sidechain compression effect.

    Args:
        music_path: Background music file
        narration_path: Narration audio file (used as trigger)
        output_path: Output ducked music file
        duck_level: Volume multiplier during speech (0.25 = 25% volume)
    """
    # FFmpeg sidechaincompress filter
    # This detects audio in narration_path and reduces music_path volume accordingly
    cmd = [
        "ffmpeg",
        "-y",
        "-i", music_path,
        "-i", narration_path,
        "-filter_complex",
        f"[0:a][1:a]sidechaincompress=threshold=0.02:ratio=20:attack=200:release=1000:makeup={duck_level}[out]",
        "-map", "[out]",
        "-codec:a", "aac",
        "-b:a", "192k",
        output_path
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"Music ducked: {output_path}")
        return output_path
    except subprocess.CalledProcessError:
        # Fallback: just lower the volume without sidechain (simpler, always works)
        print("Sidechaincompress failed, using simple volume reduction...")
        cmd = [
            "ffmpeg",
            "-y",
            "-i", music_path,
            "-af", f"volume={duck_level}",
            "-codec:a", "aac",
            "-b:a", "192k",
            output_path
        ]
        subprocess.run(cmd, check=True)
        return output_path


def generate_background_music(story_text: str, duration: float, output_folder: str = "output") -> str:
    """
    Main function: Generate background music track for the story.

    Process:
    1. Analyze story tone
    2. Select appropriate music track
    3. Normalize to match duration

    Returns: path to processed music file
    """
    tone = analyze_story_tone(story_text)
    print(f"🎵 Story tone detected: {tone}")

    # Select music
    raw_music = select_music_track(tone)
    print(f"🎵 Selected track: {os.path.basename(raw_music)}")

    # Normalize length
    os.makedirs(output_folder, exist_ok=True)
    output_music = os.path.join(output_folder, f"music_{tone}_{int(duration)}s.mp3")
    normalize_music_length(raw_music, duration, output_music)

    return output_music
