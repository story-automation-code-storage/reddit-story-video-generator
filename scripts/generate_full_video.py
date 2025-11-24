import os
import sys
import random
import subprocess
from datetime import datetime
from dotenv import load_dotenv

from openai import OpenAI

from scripts.story_generator import generate_story
from scripts.clip_scheduler import build_clip_schedule, SchedulerConfig
from scripts.ffmpeg_builder import render_background

import gspread
from oauth2client.service_account import ServiceAccountCredentials


# ------------------------------------------------------
# ENV / OPENAI
# ------------------------------------------------------

load_dotenv()
client = OpenAI()


# ------------------------------------------------------
# GOOGLE SHEETS - GAME LIBRARY
# ------------------------------------------------------

def load_game_library():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "config/service_account.json", scope
    )

    gs = gspread.authorize(creds)
    sh = gs.open("story-generator")
    ws = sh.worksheet("game_library")

    rows = ws.get_all_records()

    game_map = {}
    for r in rows:
        game_id = str(r["game_id"]).strip()
        game_map[game_id] = {
            "game_name": r["game_name"],
            "facts": [
                r["fact_1"],
                r["fact_2"],
                r["fact_3"],
                r["fact_4"],
                r["fact_5"],
            ],
            "ratio": float(r["ratio"]),
        }

    return game_map


def choose_game(game_map):
    keys = list(game_map.keys())
    weights = [game_map[k]["ratio"] for k in keys]
    return random.choices(keys, weights=weights, k=1)[0]


# ------------------------------------------------------
# AUDIO LENGTH (FFPROBE)
# ------------------------------------------------------

def get_ffprobe_path():
    ffmpeg = os.getenv("FFMPEG_PATH", "").strip().replace("/", "\\")
    ffmpeg = ffmpeg.strip('"').strip("'")

    if ffmpeg.lower().endswith("ffmpeg.exe"):
        return ffmpeg[:-len("ffmpeg.exe")] + "ffprobe.exe"

    return "C:\\ffmpeg\\bin\\ffprobe.exe"


def get_audio_duration(path):
    ffprobe = get_ffprobe_path()
    cmd = [
        ffprobe,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 0.0


# ------------------------------------------------------
# GAMEPLAY CLIPS
# ------------------------------------------------------

def list_clips_for_game(game_id):
    folder = "assets/gameplay_normalized"
    if not os.path.isdir(folder):
        return []
    return sorted([
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().startswith(game_id.lower()) and f.lower().endswith(".mp4")
    ])


# ------------------------------------------------------
# TTS – Voice Selection (Smart)
# ------------------------------------------------------

def choose_voice_for_story(story_text: str, channel_id: str | None = None) -> str:
    """
    Heuristic voice selection based on story content.
    This is intentionally simple and biased toward natural, clear voices.
    """

    s = story_text.lower()

    # Very rough gender inference based on relational cues
    male_cues = ["as a guy", "i'm a guy", "my girlfriend", "my wife", "as a husband", "my son"]
    female_cues = ["as a girl", "i'm a girl", "my boyfriend", "my husband", "as a wife", "my daughter"]

    if any(c in s for c in male_cues):
        inferred_gender = "male"
    elif any(c in s for c in female_cues):
        inferred_gender = "female"
    else:
        inferred_gender = "neutral"

    # Tone inference based on emotion keywords
    dark_cues = ["terrified", "panicked", "breaking down", "trauma", "stalking", "creepy", "dark", "anxiety"]
    fun_cues = ["funniest", "laughing", "joked", "ridiculous", "couldn't stop laughing", "hilarious"]
    warm_cues = ["heartwarming", "kind", "gentle", "sweet", "wholesome", "grateful", "comforting"]

    if any(k in s for k in dark_cues):
        tone = "dark"
    elif any(k in s for k in fun_cues):
        tone = "fun"
    elif any(k in s for k in warm_cues):
        tone = "warm"
    else:
        tone = "neutral"

    # Map (gender, tone) to OpenAI built-in voices
    # Voices: alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer
    if inferred_gender == "male":
        if tone == "dark":
            return "onyx"   # deeper, serious
        elif tone == "fun":
            return "echo"   # lighter, energetic
        elif tone == "warm":
            return "alloy"  # friendly, warm
        else:
            return "echo"   # default male-ish narrator
    elif inferred_gender == "female":
        if tone == "dark":
            return "coral"  # serious, clear
        elif tone == "fun":
            return "shimmer"  # brighter, playful
        elif tone == "warm":
            return "fable"  # soft, empathetic
        else:
            return "nova"   # neutral clear female-ish
    else:
        # Neutral / ambiguous: pick voices that don't lean too hard either way
        if tone == "dark":
            return "onyx"
        elif tone == "fun":
            return "alloy"
        elif tone == "warm":
            return "fable"
        else:
            return "sage"   # calm, neutral-ish

def build_tts_instructions(story_text: str, channel_id: str | None = None) -> str:
    """
    Build a short TTS style instruction string based on tone.
    This is optional flavor; keep it simple so it doesn't over-control.
    """
    s = story_text.lower()

    if any(k in s for k in ["camping", "stalking", "creepy", "we need to leave", "gut feeling"]):
        return "Tell this like a suspenseful but grounded story, with calm intensity."
    if any(k in s for k in ["mother-in-law", "karen", "wedding", "family drama"]):
        return "Tell this with calm, slightly sarcastic humor."
    if any(k in s for k in ["kid", "my son", "my daughter", "toddler", "classroom"]):
        return "Tell this with light, playful energy."
    if any(k in s for k in ["terminal", "cancer", "last time", "funeral"]):
        return "Tell this slowly and gently, with empathy."
    # Default
    return "Tell this like a natural Reddit story narration, casual and conversational."


def tts_generate_mp3(text: str, mp3_path: str, channel_id: str | None = None):
    voice = choose_voice_for_story(text, channel_id=channel_id)
    instructions = build_tts_instructions(text, channel_id=channel_id)

    # Choose highest-quality model available for offline rendering.
    # If tts-1-hd is not enabled on your account, fall back to gpt-4o-mini-tts.
    TTS_MODEL = "tts-1-hd"  # change to "gpt-4o-mini-tts" if you get model errors

    with client.audio.speech.with_streaming_response.create(
        model=TTS_MODEL,
        voice=voice,
        input=text,
        # You can tweak speed; 1.7 is quite fast, good for Shorts
        speed=1.7,
        instructions=instructions,
    ) as response:
        response.stream_to_file(mp3_path)

    print(f"TTS model       = {TTS_MODEL}")
    print(f"TTS voice       = {voice}")
    print(f"TTS instructions= {instructions}")
    print("Saved MP3:", mp3_path)

# ------------------------------------------------------
# MERGE AUDIO + VIDEO
# ------------------------------------------------------

def mux_audio_video(bg_path, audio_path, final_path):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", bg_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        final_path,
    ]
    subprocess.run(cmd, check=True)
    print("Merged:", final_path)


# ------------------------------------------------------
# MAIN PIPELINE
# ------------------------------------------------------

def generate_full_video(channel_id):

    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("=== STEP 1: STORY ===")
    result = generate_story(channel_id)
    hook = result["hook"]
    story = result["story"]
    print("HOOK:", hook)

    print("=== STEP 2: TTS ===")
    audio_path = f"output/{channel_id}_{timestamp}_AUDIO.mp3"
    tts_generate_mp3(story, audio_path, channel_id=channel_id)

    print("=== STEP 3: AUDIO LENGTH ===")
    duration = get_audio_duration(audio_path)
    print("Length:", duration)

    print("=== STEP 4: GAME ===")
    game_map = load_game_library()
    game_id = choose_game(game_map)
    clips = list_clips_for_game(game_id)
    print(f"Selected game: {game_id}, clips = {len(clips)}")

    if not clips:
        raise RuntimeError("No clips found for game.")

    print("=== STEP 5: SCHEDULE ===")
    config = SchedulerConfig(
        min_seg=5,
        max_seg=7,
        shuffle_clips=True,
        rollover_strategy="advance",
    )
    schedule = build_clip_schedule(clips, duration, config=config)
    print("Segments:", len(schedule))

    print("=== STEP 6: RENDER BG ===")
    bg_path = f"output/{channel_id}_{timestamp}_BG.mp4"
    render_background(schedule, bg_path)

    print("=== STEP 7: MERGE ===")
    final_path = f"output/{channel_id}_{timestamp}_FINAL.mp4"
    mux_audio_video(bg_path, audio_path, final_path)

    print("DONE:", final_path)
    return final_path


# ------------------------------------------------------
# CLI ENTRY
# ------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.generate_full_video <channel_id>")
        sys.exit(1)

    generate_full_video(sys.argv[1])
