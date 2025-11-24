import random
import subprocess
import json
from dataclasses import dataclass


# ------------------------------------------------------
# CONFIG
# ------------------------------------------------------

@dataclass
class SchedulerConfig:
    min_seg: int = 9      # updated from 5
    max_seg: int = 11     # updated from 7
    shuffle_clips: bool = True
    rollover_strategy: str = "advance"


# ------------------------------------------------------
# CLIP DURATION
# ------------------------------------------------------

def get_clip_duration(path):
    \"\"\"Reads duration of a video clip via ffprobe.\"\"\"
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_streams",
        path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    info = json.loads(result.stdout or "{}")

    streams = info.get("streams", [])
    for s in streams:
        if s.get("codec_type") == "video":
            try:
                return float(s.get("duration", 0.0))
            except:
                return 0.0

    return 0.0


# ------------------------------------------------------
# SCHEDULER
# ------------------------------------------------------

def pick_segment_start(clip_duration, seg_len):
    \"\"\"
    Returns the selected start time based on rules:
      25% start of clip
      25% end of clip
      50% random position
    \"\"\"

    if clip_duration <= seg_len:
        return 0.0

    roll = random.random()

    # 25%: start of clip
    if roll < 0.25:
        return 0.0

    # 25%: end of clip
    elif roll < 0.50:
        return max(0.0, clip_duration - seg_len)

    # 50%: random position
    else:
        return random.uniform(0.0, clip_duration - seg_len)


def build_clip_schedule(clips, target_length, config: SchedulerConfig):
    \"\"\"
    Generates:
    [
      {
        "clip": str,
        "in": float,
        "out": float,
        "duration": float,
        "timeline_start": float
      }
    ]
    \"\"\"

    if config.shuffle_clips:
        random.shuffle(clips)

    schedule = []
    total_time = 0.0
    clip_i = 0

    # Prevent infinite loops if clips are invalid
    if not clips:
        raise RuntimeError("No gameplay clips available.")

    while total_time < target_length:
        clip = clips[clip_i % len(clips)]
        duration = get_clip_duration(clip)

        # if video cannot be read, skip
        if duration <= 0:
            clip_i += 1
            continue

        seg_len = random.randint(config.min_seg, config.max_seg)

        # Choose segment start based on your new rules
        seg_start = pick_segment_start(duration, seg_len)

        schedule.append({
            "clip": clip,
            "in": seg_start,
            "out": seg_start + seg_len,
            "duration": seg_len,
            "timeline_start": total_time,
        })

        total_time += seg_len
        clip_i += 1

    return schedule
