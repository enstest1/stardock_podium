# PROJECTSTRUCTURE.md

> **Project Folder & File Structure Overview**

This document explains the layout of the AI Podcast Generation System project. It describes what each folder and file is for, so new developers can quickly understand where to find and put things.

---

## Project Directory Tree

```
.
├── main.py                  # Project entry point, environment checks, setup
├── cli_entrypoint.py        # CLI command definitions and routing
├── requirements.txt         # Python dependencies
├── .env                     # API keys and config (not in version control)
├── Docs/
│   ├── HOWTORUN.md          # Step-by-step usage guide
│   ├── WORKFLOW.md          # Technical workflow and architecture reference
│   └── PROJECTSTRUCTURE.md  # This file
├── books/                   # Ingested EPUBs and processed book data
│   └── <book_id>/           # Each book gets its own folder
├── analysis/                # Book style/content analysis results
├── episodes/                # All episode data
│   └── <episode_id>/        # Each episode gets its own folder
│       ├── structure.json   # Episode outline/structure
│       ├── script.json      # Episode script
│       ├── metadata.json    # Episode metadata
│       ├── quality_check.json # Quality check results
│       └── audio/           # Audio files for the episode
│           ├── scene_XX/    # Per-scene audio folders
│           ├── partial_episode.mp3 # Concatenated audio
│           └── ...
├── voices/                  # Voice registry and ElevenLabs mappings
│   └── registry.json        # Character-to-voice mapping
├── data/                    # General app data (config, tags, series, etc.)
│   └── mem0_config.json     # Mem0 vector DB config
├── logs/                    # Application log files
├── temp/                    # Temporary files during processing
├── assets/                  # Sound effects, music, ambience
├── script_editor.py         # Script editing and manipulation
├── story_structure.py       # Episode/season structure and outline logic
├── audio_pipeline.py        # Audio generation, mixing, and post-processing
├── voice_registry.py        # Voice management and ElevenLabs integration
├── book_style_analysis.py   # Book style and content analysis
├── epub_processor.py        # EPUB reading and parsing
├── mem0_client.py           # Mem0 vector DB wrapper
├── reference_memory_sync.py # Syncs book/episode memories to Mem0
├── episode_memory.py        # Extracts and stores episode memories
├── episode_metadata.py      # Episode tags, series, and feed management
├── quality_checker.py       # Script/audio quality analysis
├── register_voices.py       # CLI tool for assigning voices
├── concat_audio.py          # Script for concatenating audio files
├── tests/                   # Unit and integration tests
│   └── ...
└── ... (other files)
```

---

## Directory & File Descriptions

- **main.py**: Starts the app, checks environment, sets up logging and directories.
- **cli_entrypoint.py**: Handles all CLI commands and argument parsing.
- **requirements.txt**: Lists all Python packages needed.
- **.env**: Stores API keys and secrets (not checked into git).

### Docs/
- **HOWTORUN.md**: Beginner-friendly usage guide.
- **WORKFLOW.md**: Deep technical workflow and architecture.
- **PROJECTSTRUCTURE.md**: This file.

### books/
- Each subfolder is a processed book, with extracted text and metadata.

### analysis/
- Stores results of book style/content analysis.

### episodes/
- Each subfolder is an episode, containing all data and audio for that episode.
- **audio/**: Contains all generated audio for the episode, including per-scene and full-episode files.

### voices/
- **registry.json**: Maps character names to ElevenLabs voice IDs.

### data/
- General app data, config, and registry files.

### logs/
- Log files for debugging and auditing.

### temp/
- Temporary files created during processing (safe to delete).

### assets/
- Sound effects, music, and ambience used in audio generation.

### tests/
- Unit and integration tests for the codebase.

### Core Python Modules
- Each `.py` file in the root handles a specific domain (see comments in the tree above).

---

**Tip:**
- When adding new features, put code in the module whose responsibility matches the new logic.
- For new data types, create a new folder in `data/` or `episodes/` as needed.

---

This structure keeps the project organized, modular, and easy to maintain for both new and experienced developers.
