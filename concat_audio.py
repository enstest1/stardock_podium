import ffmpeg
import os
from pathlib import Path

def concat_audio_files(input_list_file, output_file):
    try:
        # Read the input file list
        with open(input_list_file, 'r') as f:
            files = [line.strip() for line in f if line.strip()]
        
        # Create a temporary file with the list of files
        with open('temp_list.txt', 'w') as f:
            for file in files:
                # Extract the path from the line (handles both 'file ...' and just the path)
                if file.startswith("file "):
                    file_path = file[5:].strip().strip("'\"")
                else:
                    file_path = file.strip().strip("'\"")
                # Convert to forward slashes
                file_path = str(Path(file_path)).replace('\\', '/')
                f.write(f"file '{file_path}'\n")
        
        # Use ffmpeg to concatenate the files with explicit audio parameters
        stream = ffmpeg.input('temp_list.txt', format='concat', safe=0)
        stream = ffmpeg.output(stream, output_file,
                             acodec='libmp3lame',  # Use MP3 codec
                             audio_bitrate='192k',  # Higher bitrate for better quality
                             ar=44100,  # Sample rate
                             ac=2)  # Stereo audio
        ffmpeg.run(stream, overwrite_output=True)
        
        # Clean up temporary file
        os.remove('temp_list.txt')
        
        print(f"Successfully concatenated audio files to {output_file}")
        return True
    except Exception as e:
        print(f"Error concatenating audio files: {e}")
        return False

if __name__ == "__main__":
    input_file = "episodes/ep_988afb7c/audio/episode_concat.txt"
    output_file = "episodes/ep_988afb7c/audio/partial_episode.mp3"
    concat_audio_files(input_file, output_file) 