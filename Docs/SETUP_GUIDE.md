# Super Simple Setup Guide

## Step 1: Install Python
Make sure you have Python 3.8 or newer installed on your Windows 10 computer.

## Step 2: Get the Code
1. Download all these files to a folder on your computer

## Step 3: Install Requirements
1. Open Command Prompt 
2. Navigate to the folder with the code
3. Run: `pip install -r requirements.txt`

## Step 4: Install FFmpeg
1. Download FFmpeg from: https://ffmpeg.org/download.html
2. Extract the files
3. Add the bin folder to your Windows PATH

## Step 5: Set Up API Keys
Create a file named `.env` in the same folder with this content:
```
OPENAI_API_KEY=your_openai_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
MEM0_API_KEY=your_mem0_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
```

Replace the "your_xxx_key_here" parts with your actual API keys.

## Step 6: First Run
1. Open Command Prompt
2. Navigate to the folder with the code
3. Run: `python main.py`

## Step 7: Start Creating
1. Add a sci-fi book: `python main.py ingest path/to/book.epub`
2. Register voices: `python main.py register-voice "Captain Kirk" your_elevenlabs_voice_id`
3. Create an episode: `python main.py generate-episode --title "Space Adventure"`
4. Make audio: `python main.py generate-audio your_episode_id`

## Folder Structure
The program will automatically create these folders:
- `books/` - Your uploaded books
- `analysis/` - Analysis of book styles
- `episodes/` - Generated episode scripts
- `audio/` - Generated audio files
- `voices/` - Saved voice information
- `data/` - Program data
- `temp/` - Temporary files

## Get Help
Type `python main.py --help` to see all available commands