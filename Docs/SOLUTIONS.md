# Solution: Robust Episode Generation Workflow

## Overview
To resolve the workflow blocker, the CLI and backend logic must be enhanced to allow users to generate characters and scenes independently, and to make the script generation process robust to missing data. This will restore full automation and usability to the episode generation pipeline.

## Proposed Enhancements

### 1. Add CLI Commands for Character and Scene Generation
- **New Command:** `generate-characters <episode_id>`
  - Generates a cast of characters for the specified episode and updates `structure.json`.
- **New Command:** `generate-scenes <episode_id>`
  - Generates scene outlines for the specified episode (requires characters to exist) and updates `structure.json`.
- **Usage Example:**
  ```sh
  python main.py generate-characters ep_12345678
  python main.py generate-scenes ep_12345678
  ```
- **Rationale:**
  - Allows users to progress step-by-step and script/batch the process.
  - Makes the workflow explicit and debuggable.

### 2. Make `edit-script` Robust to Missing Scenes/Characters
- **Enhance Logic:**
  - If `edit-script` is called and scenes or characters are missing, automatically generate them before proceeding to script generation.
- **Rationale:**
  - Allows a single command to handle the full workflow for most users.
  - Reduces user confusion and manual intervention.

### 3. Fix Audio Generation Pipeline
- **Character Name Sanitization:**
  ```python
  def sanitize_filename(name: str) -> str:
      """Convert character name to safe filename."""
      return ''.join(c for c in name.lower().replace(' ', '_') 
                    if c.isalnum() or c == '_')
  ```
  - Apply consistent sanitization across all file operations
  - Remove all special characters except underscores
  - Use sanitized names in both file generation and references

- **Scene Audio Mixing:**
  ```python
  def _mix_scene_audio(self, line_clips: List[AudioClip], 
                      ambience_clip: Optional[AudioClip],
                      output_file: Path) -> float:
      # Use absolute paths in concat file
      with open(concat_file, 'w') as f:
          for clip in line_clips:
              f.write(f"file '{os.path.abspath(clip.path)}'\n")
      
      # Remove cwd argument from ffmpeg.run()
      ffmpeg.input(str(concat_file), format='concat', safe=0)
          .output(str(output_file), c='copy')
          .overwrite_output()
          .run()
  ```
  - Use absolute paths in all FFmpeg operations
  - Remove working directory manipulation
  - Add robust error handling and logging

- **Episode Assembly:**
  ```python
  def _assemble_episode(self, episode_id: str, scene_results: List[Dict[str, Any]],
                       intro_file: Optional[Path], outro_file: Optional[Path],
                       audio_dir: Path) -> Optional[Path]:
      # Verify all required files exist
      for scene in scene_results:
          if not Path(scene['audio_file']).exists():
              logger.error(f"Missing scene audio: {scene['audio_file']}")
              return None
      
      # Use absolute paths in concat file
      with open(concat_file, 'w') as f:
          for scene in sorted(valid_scenes, key=lambda s: s.get("scene_index", 0)):
              f.write(f"file '{os.path.abspath(scene['audio_file'])}'\n")
  ```
  - Add file existence checks before assembly
  - Use absolute paths consistently
  - Improve error reporting and recovery

### 4. Add Robust Error Handling
- **Implement Error Recovery:**
  - Add retry logic for failed audio generation
  - Implement cleanup of partial files on failure
  - Add detailed error logging and reporting
  - Create recovery points for long-running operations

- **Add Validation Steps:**
  - Verify all required files exist before operations
  - Check file permissions and disk space
  - Validate audio file integrity
  - Ensure consistent file naming across operations

### 5. Update Documentation
- **Update `SETUP_GUIDE.md` and CLI help text** to reflect the new commands and workflow.
- **Add troubleshooting section** for common errors and their solutions.
- **Document audio generation pipeline** with examples and best practices.
- **Add cross-platform compatibility notes** for FFmpeg operations.

### 6. Add Validation for Continuity and Audio-Ready Formatting
- **Enhancement:**
  - Add validation steps before audio generation to ensure that:
    - Narrative continuity is maintained by checking for relevant memories and references in the episode structure and script.
    - Script and structure files are formatted according to the requirements of the audio pipeline (e.g., correct character names, fields present, no malformed lines).
- **Rationale:**
  - Prevents audio generation failures due to formatting issues.
  - Ensures each episode follows the ongoing story arc and character development.
  - Reduces manual debugging and increases automation reliability.

## Implementation Steps
1. **Backend:**
   - Refactor `story_structure.py` to expose `generate_character_cast` and `generate_scenes` as CLI-accessible functions.
   - Add new CLI command handlers in `cli_entrypoint.py` for `generate-characters` and `generate-scenes`.
   - Update `edit-script` logic to check for and generate missing characters/scenes as needed.
   - Implement robust file path handling in `audio_pipeline.py`.
   - Add comprehensive error handling and recovery mechanisms.

2. **Testing:**
   - Add unit and integration tests for the new commands and enhanced workflow.
   - Test edge cases (e.g., missing beats, partial data, repeated runs).
   - Add cross-platform testing for audio generation.
   - Test error recovery and cleanup procedures.

3. **Docs:**
   - Update all relevant documentation and help text.
   - Add troubleshooting guides for common issues.
   - Document the audio generation pipeline in detail.
   - Include examples of successful workflows.

## Acceptance Criteria
- Users can generate characters and scenes for any episode via CLI commands.
- Running `edit-script` on an episode with no characters or scenes will succeed (auto-generates missing data).
- The workflow is fully automatable and does not require manual JSON editing.
- Audio generation works reliably across different operating systems.
- Error handling provides clear feedback and recovery options.
- Documentation is clear and up-to-date.

## Rationale
- This approach restores the intended automation and usability of the CLI.
- It supports both step-by-step and all-in-one workflows.
- It is robust to missing or partial data, reducing user frustration and support burden.
- The audio pipeline improvements ensure reliable podcast generation.
- Cross-platform compatibility is maintained throughout the system.
