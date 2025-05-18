# Problem: Episode Generation Workflow Blocker & Audio Generation Limitations

## Context
The Stardock Podium CLI is designed to generate Star Trek-style podcast episodes using a modular workflow. The process involves ingesting books, generating an episode structure (beats), then generating characters, scenes, and finally a script. The main commands available are:
- `generate-episode`: Creates the episode structure and beats.
- `edit-script`: Edits or generates the script for an episode.

## Symptoms
- After running `generate-episode`, the resulting `structure.json` contains only the beats; the `characters` and `scenes` arrays are empty.
- Running `edit-script` on such an episode fails with errors like:
  - `Script file not found: episodes/<episode_id>/script.json`
  - `Script not found for episode: <episode_id>`
- There are no CLI commands to generate characters or scenes directly.
- The user is blocked from progressing to script generation unless they manually edit the structure file to add scenes.
- **Episodes may lose narrative continuity if memory extraction or referencing fails, resulting in disconnected storylines across episodes.**
- **If script or structure formatting is inconsistent or does not match audio pipeline requirements, audio generation may fail or produce mismatched voices.**

## Audio Generation Pipeline Issues
1. **ElevenLabs API Credit Exhaustion**
   - ElevenLabs credits have run out, blocking further audio generation.
   - Need to identify and integrate a high-quality open-source TTS (text-to-speech) alternative to continue generating podcast audio.
   - Must ensure the new TTS solution supports multiple voices and is scriptable for batch processing.

2. **Character Name Sanitization**
   - Character names with special characters (e.g., `Aria T'Vel`) caused issues in audio file generation
   - Filenames were not properly sanitized, leading to mismatches between generated files and references
   - FFmpeg failed to find audio files due to inconsistent naming

3. **Scene Audio Mixing**
   - Scene audio mixing failed due to incorrect file paths in concat files
   - Relative paths were used instead of absolute paths
   - FFmpeg's working directory was incorrectly set, causing file not found errors

4. **Episode Assembly**
   - Final episode assembly failed due to missing scene audio files
   - Concatenation file contained incorrect paths
   - Some scenes were skipped or failed to generate audio

5. **File Access and Playback Issues**
   - Some generated audio files could not be played or moved due to file system errors (e.g., 0-byte files, locked files, or path issues)
   - Users encountered errors when trying to open or copy files, especially after conversion steps

## Root Cause
- The CLI does not expose commands for generating characters or scenes independently.
- The `edit-script` command expects scenes to already exist in the episode structure, but does not generate them if missing.
- The workflow assumes that scenes (and possibly characters) are present, but the only way to get them is via internal methods not exposed to the CLI.
- Audio pipeline lacks robust error handling and path management
- Character name sanitization was incomplete, leading to file system issues
- FFmpeg operations were not properly configured for cross-platform compatibility
- **Audio generation is currently blocked due to exhausted ElevenLabs credits and lack of an open-source TTS fallback.**
- **Breaks in memory extraction or referencing can disrupt narrative continuity.**
- **Improper script/structure formatting can block or corrupt audio generation.**

## Why This Is a Blocker
- Users following the documented workflow cannot generate a script for a new episode without manually editing JSON files.
- This breaks the intended automation and usability of the CLI.
- It is not obvious to users that they need to manually add scenes or characters, leading to confusion and frustration.
- The lack of CLI commands for these steps prevents scripting or batch processing of episode generation.
- Audio generation failures prevent the creation of complete podcast episodes
- Inconsistent file naming and path handling make the system unreliable
- **No audio can be generated until a new TTS solution is integrated.**

## Example
1. User runs:
   ```sh
   python main.py generate-episode --title "Shadows of the Prophets" --theme "A mysterious signal from Bajor..."
   ```
2. The episode is created, but `characters` and `scenes` are empty in `structure.json`.
3. User runs:
   ```sh
   python main.py edit-script <episode_id>
   ```
4. The command fails with errors about missing script or scenes.
5. Even after fixing script generation, audio generation fails due to:
   - Character name issues (e.g., `Aria T'Vel` → `aria_t'vel.mp3`)
   - Scene mixing failures (incorrect paths)
   - Episode assembly errors (missing files)
   - **Audio generation blocked by lack of ElevenLabs credits**

## Related Errors
- `Script file not found: episodes/<episode_id>/script.json`
- `Script not found for episode: <episode_id>`
- No CLI command for generating characters or scenes
- `Impossible to open 'episodes/<episode_id>/audio/scene_XX/scene_audio.mp3'`
- `Error mixing scene audio: run() got an unexpected keyword argument 'cwd'`
- `episode_concat.txt: No such file or directory`
- **ElevenLabs API quota exceeded or credits exhausted**
- `File not found` or `0 bytes` errors when moving or playing audio files

## Impact
- Blocks all users from generating scripts for new episodes unless they manually edit files or modify the codebase
- Prevents full automation of the episode generation pipeline
- Audio generation failures prevent the creation of complete podcast episodes
- Inconsistent behavior across different operating systems
- Poor error handling makes debugging difficult
- Manual intervention required at multiple steps
- **No further audio can be generated until a new TTS solution is found and integrated**
