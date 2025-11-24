# PHASE 2: AUDIO + VISUAL ENHANCEMENTS BLUEPRINT

## 🎭 Overview

This blueprint outlines the planned enhancements to the video generation pipeline:

- **🎵 Background Music Engine**: Automatic music selection and mixing
- **🔊 Sound Effects (SFX)**: Timed SFX based on story beats
- **🎨 Canva Templates**: Auto-generated thumbnails and title cards
- **💬 Auto Captions**: Burned-in animated subtitles

## 🔧 Pipeline Integration

```
generate_full_video.py (↔ CURRENT)
    ↓
    story_generator.py → story text
    ↓
    tts via audio_engine
    ↓
    clip_scheduler → gameplay selection
    ↓
    ffmpeg_builder → background render
    ↓
    NEW: music_engine → background music  (✏️ PHASE 2)
    ↓
    NEW: sfx_engine → SFX timed to story beats (✏️ PHASE 2)
    ↓
    captions_engine → burned-in subtitles (✏️ PHASE 2)
    ↓
    NEW: canva_thumbnails → fake Reddit title screenshot + thumbnail (✏️ PHASE 2)
    ↓
    final mux
```

## 🎯 Features to Implement

### 1. Background Music Engine

**Goal**: Automatically choose and mix background music that matches the emotional tone of the story.

**How it works**:
- Emotion analysis of story (reuse gender/tone classifier)
- Map tone → soundtrack folder
  - dark → suspense
  - fun → upbeat
  - warm → mellow
  - neutral → chill
- Normalize track length to match story audio using ffmpeg
- Duck volume during speech (sidechain-like effect)

```python
scripts/audio/music_engine.py
```

**Pipeline integration**:
```python
music_path = music_engine.generate_music(story, duration)
mux_audio_video_and_music(bg_path, audio_path, music_path)
```

### 2. Sound Effects Engine (SFX)

**Goal**: Use story beats to trigger precise SFX moments to increase retention.

**Sources**:
```python
assets/sfx/
    gasp.mp3
    door_knock.mp3
    notification.mp3
    conflict_hit.mp3
    reveal_sting.mp3
    laugh.mp3
```

**How it works**:
- Parse story into beats using Lightweight NLP
- Identify keywords: "conflict", "reveal", "twist", escalation moments
- Place SFX at timestamps using approximate WPM timing
- Output: layered SFX audio track

```python
scripts/audio/sfx_engine.py
```

**Pipeline integration**:
```python
sfx_path = sfx_engine.generate_sfx(story, audio_path)
mux_three_audio(bg_video, narration_mp3, music_mp3, sfx_mp3)
```

### 3. Canva Templates

**Goal**: Generate branding assets automatically:
- Thumbnail template
- Fake Reddit header screenshot
- Story title card (optional)

Use Canva's REST API or composio canva-automation tool:
- Create template once
- Swap text, images automatically
- Export PNG/JPEG

**Outputs**:
```
output/<id>_thumbnail.png
output/<id>_reddit_screenshot.png
```

**What to automate**:
- Insert story hook as title
- Insert OP username randomly
- Add subreddit name (AskReddit)
- Background gradient or pattern
- Optional: story mood color palette

```python
scripts/visual/canva_thumbnails.py
```

**Pipeline integration**:
```python
thumbnail_path = canva_thumbnails.generate_thumbnail(hook_text)
reddit_img_path = canva_thumbnails.generate_reddit_screenshot(hook_text)
```

### 4. Auto Captions Engine

**Goal**: Burn animated captions into final video using ffmpeg.

**Process**:
- Split story into timed captions using TTS audio duration
- Generate .srt file
- Use ffmpeg filters for caption styling:
  - bold white text
  - black border or drop-shadow
  - stroke=3
  - size=42px
- Burn into gameplay background video

```python
scripts/captions/captions_engine.py
scripts/captions/srt_builder.py
```

**Pipeline integration**:
```python
captioned_bg = captions_engine.apply_captions(bg_path, story, audio_path)
# Then captioned_bg replaces bg_path in mux step
```

## 📋 Updated Pipeline Flow

Your new `generate_full_video` will follow:

1. generate story
2. TTS to mp3
3. compute duration
4. pick gameplay clips
5. build gameplay background
6. **generate background music (NEW)**
7. **generate SFX layers (NEW)**
8. **burn captions (NEW)**
9. **generate Canva thumbnail + reddit screenshot (NEW)**
10. merge narration + music + SFX + video
11. output final MP4

## 📁 Files to Add

### Audio
- `scripts/audio/music_engine.py`
- `scripts/audio/sfx_engine.py`

### Captions
- `scripts/captions/captions_engine.py`
- `scripts/captions/srt_builder.py`

### Visual (Canva)
- `scripts/visual/canva_thumbnails.py`

### Pipeline
- modifications to `generate_full_video.py`
- minor updates to `ffmpeg_builder.py`

## 🚀 Implementation Status

- [x] Core video pipeline
- [ ] Background music engine
- [ ] Sound effects engine
- [ ] Auto captions
- [ ] Canva thumbnail generation
- [ ] Full integration testing

---

**Ready to implement!** Follow this blueprint to add Phase 2 features systematically.
