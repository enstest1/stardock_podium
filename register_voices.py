#!/usr/bin/env python
"""
Script to register voices for Stardock Podium characters.
"""

import os
from dotenv import load_dotenv
from voice_registry import VoiceRegistry

# Load environment variables
load_dotenv()

# Character voice descriptions
CHARACTER_VOICES = [
    {
        "name": "Aria T'Vel",
        "description": "A Vulcan female voice that is smooth, calm, and precise in articulation. The voice should have an undercurrent of warmth that suggests a deeper understanding of emotion, while maintaining the characteristic Vulcan logical tone. The voice should be clear and measured, with perfect enunciation.",
        "settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
    },
    {
        "name": "Jalen",
        "description": "A male Trill voice that is warm and enthusiastic, carrying the wisdom of multiple lifetimes through the symbiont. The voice should have a natural eagerness that can accelerate when excited, while maintaining a sense of ancient knowledge. The tone should be friendly but authoritative, with a slight musical quality.",
        "settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
    },
    {
        "name": "Naren",
        "description": "A female Bajoran voice that is strong and confident, with the ability to shift between commanding authority and spiritual serenity. The voice should carry the weight of experience and resilience, with a slight accent that reflects her Bajoran heritage. The tone should be firm but compassionate.",
        "settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
    },
    {
        "name": "Elara",
        "description": "A female Caitian voice that is softly musical with a purring undertone. The voice should be soothing and gentle, with a playful lilt that can become serious when needed. The tone should reflect her species' feline nature while maintaining clear, professional articulation.",
        "settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
    },
    {
        "name": "Sarik",
        "description": "A male El-Aurian voice that is gentle and reflective, carrying an aura of wisdom beyond his years. The voice should be deliberate and thoughtful, with a comforting, almost lyrical quality. The tone should reflect his species' long lifespan and natural empathy.",
        "settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }
]

def main():
    """Create and register voices for all characters."""
    print("Creating and registering voices for characters...")
    
    registry = VoiceRegistry()
    
    for voice_data in CHARACTER_VOICES:
        print(f"\nCreating voice for {voice_data['name']}...")
        result = registry.create_voice_from_description(
            name=voice_data['name'],
            description=voice_data['description']
        )
        
        if "error" in result:
            print(f"Error creating voice for {voice_data['name']}: {result['error']}")
        else:
            print(f"Successfully created and registered voice for {voice_data['name']}")
            # Update voice settings
            if 'settings' in voice_data:
                registry.update_voice(
                    result['voice_registry_id'],
                    {'settings': voice_data['settings']}
                )
                print(f"Updated voice settings for {voice_data['name']}")
    
    print("\nVoice creation and registration complete!")

if __name__ == "__main__":
    main() 