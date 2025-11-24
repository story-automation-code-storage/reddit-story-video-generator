"""
SRT Builder - Generate timed .srt subtitle files from story text and audio.
"""

import os
import re
from datetime import timedelta


def format_srt_time(seconds: float) -> str:
    """Convert seconds to SRT timestamp format: HH:MM:SS,mmm"""
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    secs = int(td.total_seconds() % 60)
    millis = int((td.total_seconds() % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def split_into_caption_chunks(story_text: str, max_words_per_chunk: int = 6) -> list:
    """
    Split story text into caption chunks.
    Each chunk should be short for readability (3-6 words ideal for TikTok/Shorts).

    Returns: list of caption strings
    """
    # Split by sentences first
    sentences = re.split(r'[.!?]+', story_text)
    chunks = []

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        words = sentence.split()

        # Split into chunks of max_words_per_chunk
        for i in range(0, len(words), max_words_per_chunk):
            chunk = ' '.join(words[i:i + max_words_per_chunk])
            if chunk:
                chunks.append(chunk)

    return chunks


def generate_srt_file(story_text: str, audio_duration: float, output_path: str, words_per_second: float = 2.5):
    """
    Generate .srt subtitle file from story text.

    Args:
        story_text: Full story text
        audio_duration: Total duration of the narration audio (seconds)
        output_path: Path to save .srt file
        words_per_second: Approximate speaking rate (used to time captions)

    The timing is approximate based on total word count and audio duration.
    For perfect sync, you'd need word-level timestamps from the TTS API.
    """
    chunks = split_into_caption_chunks(story_text, max_words_per_chunk=5)

    if not chunks:
        return

    # Calculate timing for each chunk
    total_words = sum(len(chunk.split()) for chunk in chunks)
    actual_wps = total_words / audio_duration if audio_duration > 0 else words_per_second

    srt_entries = []
    current_time = 0.0

    for idx, chunk in enumerate(chunks, start=1):
        word_count = len(chunk.split())
        duration = word_count / actual_wps

        start_time = current_time
        end_time = min(current_time + duration, audio_duration)

        # Format SRT entry
        entry = f"{idx}\n{format_srt_time(start_time)} --> {format_srt_time(end_time)}\n{chunk}\n"
        srt_entries.append(entry)

        current_time = end_time

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(srt_entries))

    print(f"✅ Generated SRT file: {output_path} ({len(chunks)} captions)")
    return output_path
