#!/usr/bin/env python
"""
Script to list available ElevenLabs voices.
"""

import os
from dotenv import load_dotenv
from elevenlabs import ElevenLabs

# Load environment variables
load_dotenv()

def main():
    """List all available ElevenLabs voices."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("Error: ELEVENLABS_API_KEY not found in environment variables")
        return
    
    elevenlabs = ElevenLabs(api_key=api_key)
    
    try:
        voices = elevenlabs.voices.get_all()
        print("\nAvailable ElevenLabs Voices:")
        print("-" * 50)
        for voice in voices.voices:
            print(f"Name: {voice.name}")
            print(f"Voice ID: {voice.voice_id}")
            print(f"Category: {voice.category}")
            print(f"Description: {voice.labels.get('description', 'No description')}")
            print("-" * 50)
    except Exception as e:
        print(f"Error listing voices: {e}")

if __name__ == "__main__":
    main() 