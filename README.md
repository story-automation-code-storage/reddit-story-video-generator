# Reddit Story Video Generator 🎬

Automated video generation pipeline for creating viral Reddit story content with TTS narration, gameplay backgrounds, and smart story generation from proven viral templates.

## ✨ Features

- **🎯 Smart Story Generation**: Generates stories using AI that mimic proven viral Reddit story structures
- **🗣️ Advanced TTS**: Intelligent voice selection based on story tone and gender inference (using OpenAI TTS)
- **🎮 Dynamic Backgrounds**: Automated gameplay clip scheduling and rendering
- **📊 Data-Driven**: Uses Google Sheets for managing story templates, game libraries, and analytics
- **⚡ Fast Pipeline**: Optimized FFmpeg rendering for quick video generation
- **🎨 Customizable**: Modular architecture for easy customization and extension

## 🏗️ Project Structure

```
reddit-story-video-generator/
│
├── scripts/                    # Main source code
│   ├── generate_full_video.py  # Main pipeline orchestrator
│   ├── story_generator.py      # AI story generation engine
│   ├── clip_scheduler.py       # Gameplay clip scheduling logic
│   ├── ffmpeg_builder.py       # Video rendering with FFmpeg
│   ├── source_script_loader.py # Load viral story templates from Google Sheets
│   ├── source_script_index.py  # Template selection logic
│   ├── normalize_gameplay.py   # Normalize gameplay clips to 1080x1920
│   ├── game_description.py     # Generate game descriptions
│   │
│   ├── pipeline/               # Future: modular pipeline components
│   │   ├── audio_engine.py
│   │   ├── script_generator.py
│   │   ├── upload_manager.py
│   │   └── video_assembler.py
│   │
│   └── utils/                  # Utility modules
│       ├── drive_utils.py
│       ├── ffmpeg_utils.py
│       └── logger.py
│
├── config/                     # Configuration files
│   ├── settings.yaml           # Pipeline settings
│   └── service_account.json    # Google Sheets API credentials (NOT IN REPO)
│
├── assets/                     # Video assets (not tracked)
│   ├── gameplay/               # Raw gameplay footage
│   ├── gameplay_normalized/    # Processed 1080x1920 clips
│   ├── sfx/                    # Sound effects
│   └── music/                  # Background music
│
├── output/                     # Generated videos (not tracked)
│
├── engagement_patterns.json    # Analysis of viral story engagement patterns
├── story_blueprint.json        # Story archetype blueprints
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.11+
- FFmpeg installed and in PATH
- OpenAI API key
- Google Cloud Service Account (for Sheets integration)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/story-automation-code-storage/reddit-story-video-generator.git
   cd reddit-story-video-generator
   ```

2. **Install Python dependencies**
   ```bash
   pip install openai gspread oauth2client python-dotenv
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY and FFMPEG_PATH
   ```

4. **Set up Google Sheets API**
   - Create a Google Cloud project
   - Enable Google Sheets API
   - Create a service account and download JSON credentials
   - Save as `config/service_account.json`
   - Share your Google Sheet with the service account email

5. **Prepare assets**
   ```bash
   mkdir -p assets/gameplay assets/gameplay_normalized output
   # Add your gameplay clips to assets/gameplay/
   ```

6. **Normalize gameplay clips**
   ```bash
   python -m scripts.normalize_gameplay
   ```

## 📖 Usage

### Generate a Video

```bash
python -m scripts.generate_full_video <channel_id>
```

Example:
```bash
python -m scripts.generate_full_video storytales
```

### Pipeline Steps

1. **Story Generation**: AI generates a story using viral templates from Google Sheets
2. **Text-to-Speech**: Converts story to audio with intelligent voice selection
3. **Clip Scheduling**: Selects and schedules gameplay background clips
4. **Video Rendering**: Renders background video with FFmpeg
5. **Final Assembly**: Merges audio and video into final output

## 🎯 Story Generation System

The story generator uses a sophisticated template-based approach:

- **Viral Template Analysis**: Analyzes proven high-performing Reddit stories
- **Structure Mimicry**: Reproduces emotional arcs, pacing, and dramatic peaks
- **Smart Voice Selection**: Chooses appropriate TTS voice based on:
  - Gender inference (from story context)
  - Emotional tone (dark, fun, warm, neutral)
  - Delivery style instructions

## 📊 Data Sources

The system uses Google Sheets for:

- **source_scripts**: Viral story templates with metadata
- **game_library**: Available gameplay clips with selection weights
- **channels**: Channel configuration and targeting
- **trend_data**: Current trending topics and themes

## 🔧 Configuration

### `config/settings.yaml`

```yaml
openai:
  model: gpt-4.1
  temperature: 0.9

paths:
  assets: "./assets"
  output: "./output"

audio:
  loudness_target: -14
  normalize: true
```

### `.env`

```env
OPENAI_API_KEY=sk-...
FFMPEG_PATH=C:\ffmpeg\bin\ffmpeg.exe
```

## 🎨 Phase 2: Planned Enhancements

- **🎵 Background Music Engine**: Automatic music selection and mixing
- **🔊 Sound Effects**: Timed SFX based on story beats
- **💬 Auto Captions**: Burned-in animated subtitles
- **🖼️ Canva Integration**: Auto-generated thumbnails and title cards
- **📤 Upload Automation**: Direct upload to YouTube/TikTok

## 🤝 Contributing

This is a personal project, but feel free to fork and customize for your own use!

## 📝 License

MIT License - feel free to use and modify!

## ⚠️ Important Notes

- **Never commit** `config/service_account.json` or `.env` files
- **Respect API limits**: OpenAI TTS and Google Sheets have rate limits
- **Content rights**: Ensure you have rights to gameplay footage used
- **Story originality**: AI-generated stories should be reviewed for quality

## 🐛 Troubleshooting

### Common Issues

1. **FFmpeg not found**
   - Ensure FFmpeg is installed and PATH is set correctly in `.env`

2. **Google Sheets authentication error**
   - Verify `service_account.json` is present and valid
   - Check that the Sheet is shared with the service account email

3. **No clips found for game**
   - Run `normalize_gameplay.py` to process raw clips
   - Ensure clips are named with game_id prefix (e.g., `subway_001.mp4`)

4. **TTS generation fails**
   - Verify OpenAI API key is valid
   - Check API quota and billing

## 📧 Contact

For questions or issues, open a GitHub issue.

---

**Built with ❤️ for content creators** | Powered by OpenAI, FFmpeg, and Google Sheets
