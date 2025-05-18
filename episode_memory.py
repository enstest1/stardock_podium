#!/usr/bin/env python
"""
Episode Memory Module for Stardock Podium.

This module handles the storage and retrieval of episode memories,
including plot points, character developments, and continuity information.
"""

import os
import json
import logging
import time
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Local imports
from mem0_client import get_mem0_client
from story_structure import get_episode

# Setup logging
logger = logging.getLogger(__name__)

class EpisodeMemory:
    """Manages episode memory and continuity."""
    
    # Constants for memory categories
    PLOT_POINT = "plot_point"
    CHARACTER_DEVELOPMENT = "character_development"
    WORLD_BUILDING = "world_building"
    CONTINUITY = "continuity"
    RELATIONSHIP = "relationship"
    
    def __init__(self):
        """Initialize the episode memory manager."""
        self.mem0_client = get_mem0_client()
    
    def extract_memories_from_episode(self, episode_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract memory entries from an episode.
        
        Args:
            episode_id: ID of the episode
        
        Returns:
            Dictionary of memory entries by category
        """
        # Get episode data
        episode = get_episode(episode_id)
        if not episode:
            logger.error(f"Episode not found: {episode_id}")
            return {}
        
        # Extract memories by category
        memories = {
            self.PLOT_POINT: self._extract_plot_points(episode),
            self.CHARACTER_DEVELOPMENT: self._extract_character_developments(episode),
            self.WORLD_BUILDING: self._extract_world_building(episode),
            self.CONTINUITY: self._extract_continuity_points(episode),
            self.RELATIONSHIP: self._extract_relationships(episode)
        }
        
        # Save memories to database
        for category, entries in memories.items():
            for entry in entries:
                self.add_memory(
                    content=entry["content"],
                    category=category,
                    episode_id=episode_id,
                    metadata=entry.get("metadata", {})
                )
        
        return memories
    
    def _extract_plot_points(self, episode: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract plot points from an episode.
        
        Args:
            episode: Episode data
        
        Returns:
            List of plot point memory entries
        """
        plot_points = []
        
        # Extract from beats
        if "beats" in episode:
            for beat in episode["beats"]:
                plot_points.append({
                    "content": f"In episode '{episode.get('title')}', during the '{beat.get('name')}' beat: {beat.get('description')}",
                    "metadata": {
                        "beat": beat.get("name"),
                        "episode_title": episode.get("title"),
                        "episode_number": episode.get("episode_number")
                    }
                })
        
        # Extract from scenes
        if "scenes" in episode:
            for scene in episode["scenes"]:
                if "plot" in scene:
                    plot_points.append({
                        "content": f"In episode '{episode.get('title')}', scene {scene.get('scene_number', 0)}: {scene.get('plot')}",
                        "metadata": {
                            "scene_number": scene.get("scene_number", 0),
                            "beat": scene.get("beat"),
                            "episode_title": episode.get("title"),
                            "episode_number": episode.get("episode_number")
                        }
                    })
        
        return plot_points
    
    def _extract_character_developments(self, episode: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract character developments from an episode.
        
        Args:
            episode: Episode data
        
        Returns:
            List of character development memory entries
        """
        developments = []
        
        # First, get character information
        characters = {char.get("name"): char for char in episode.get("characters", [])}
        
        # Extract from script if available
        if episode.get("script") and episode["script"].get("scenes"):
            for scene in episode["script"]["scenes"]:
                # Get all dialogue lines for each character
                character_lines = {}
                for line in scene.get("lines", []):
                    if line.get("type") == "dialogue":
                        char_name = line.get("character")
                        if char_name not in character_lines:
                            character_lines[char_name] = []
                        character_lines[char_name].append(line.get("content", ""))
                
                # Look for character development in dialogue
                for char_name, lines in character_lines.items():
                    # Join lines for this character in this scene
                    char_dialogue = " ".join(lines)
                    
                    # Look for signs of character development in dialogue
                    dev_indicators = ["I've never", "I've learned", "I realize", "I understand",
                                    "I feel", "I've changed", "I used to", "I think", "I believe"]
                    
                    for indicator in dev_indicators:
                        if indicator.lower() in char_dialogue.lower():
                            # Extract the sentence containing the indicator
                            sentences = re.split(r'[.!?]+', char_dialogue)
                            relevant_sentence = next((s for s in sentences 
                                                  if indicator.lower() in s.lower()), "")
                            
                            if relevant_sentence:
                                developments.append({
                                    "content": f"Character Development for {char_name} in episode '{episode.get('title')}': {relevant_sentence.strip()}",
                                    "metadata": {
                                        "character": char_name,
                                        "episode_title": episode.get("title"),
                                        "episode_number": episode.get("episode_number"),
                                        "scene_number": scene.get("scene_number", 0)
                                    }
                                })
        
        # Add basic character introductions if this is their first appearance
        for char_name, char_data in characters.items():
            developments.append({
                "content": f"Character Introduction: {char_name} is a {char_data.get('species', 'unknown')} {char_data.get('role', 'crew member')} who appears in episode '{episode.get('title')}'. {char_data.get('personality', '')}",
                "metadata": {
                    "character": char_name,
                    "episode_title": episode.get("title"),
                    "episode_number": episode.get("episode_number"),
                    "character_role": char_data.get("role"),
                    "character_species": char_data.get("species")
                }
            })
        
        return developments
    
    def _extract_world_building(self, episode: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract world-building elements from an episode.
        
        Args:
            episode: Episode data
        
        Returns:
            List of world-building memory entries
        """
        world_building = []
        
        # Extract from scenes
        if "scenes" in episode:
            for scene in episode["scenes"]:
                if "setting" in scene:
                    world_building.append({
                        "content": f"Setting in episode '{episode.get('title')}': {scene.get('setting')}",
                        "metadata": {
                            "type": "setting",
                            "episode_title": episode.get("title"),
                            "episode_number": episode.get("episode_number"),
                            "scene_number": scene.get("scene_number", 0)
                        }
                    })
        
        # Extract from script descriptions
        if episode.get("script") and episode["script"].get("scenes"):
            for scene in episode["script"]["scenes"]:
                for line in scene.get("lines", []):
                    if line.get("type") == "description":
                        # Look for setting descriptions
                        content = line.get("content", "")
                        
                        # Only include substantial descriptions
                        if len(content) > 40 and re.search(r'(starship|planet|space|station|base|world|alien|technology)', 
                                                         content, re.IGNORECASE):
                            world_building.append({
                                "content": f"World detail from episode '{episode.get('title')}': {content}",
                                "metadata": {
                                    "type": "description",
                                    "episode_title": episode.get("title"),
                                    "episode_number": episode.get("episode_number"),
                                    "scene_number": scene.get("scene_number", 0)
                                }
                            })
        
        return world_building
    
    def _extract_continuity_points(self, episode: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract continuity points from an episode.
        
        Args:
            episode: Episode data
        
        Returns:
            List of continuity memory entries
        """
        continuity = []
        
        # Add basic episode information for continuity
        continuity.append({
            "content": f"Episode '{episode.get('title')}' (#{episode.get('episode_number')}) in series '{episode.get('series')}' deals with the theme of {episode.get('theme', 'space exploration')}.",
            "metadata": {
                "type": "episode_summary",
                "episode_title": episode.get("title"),
                "episode_number": episode.get("episode_number"),
                "series": episode.get("series")
            }
        })
        
        # Extract from script dialogue references to past events
        if episode.get("script") and episode["script"].get("scenes"):
            for scene in episode["script"]["scenes"]:
                for line in scene.get("lines", []):
                    if line.get("type") == "dialogue":
                        content = line.get("content", "")
                        
                        # Look for references to past events
                        past_indicators = ["remember when", "last time", "previously", "before",
                                          "used to", "back when", "last mission", "last episode"]
                        
                        for indicator in past_indicators:
                            if indicator.lower() in content.lower():
                                # Extract the sentence containing the indicator
                                sentences = re.split(r'[.!?]+', content)
                                relevant_sentence = next((s for s in sentences 
                                                      if indicator.lower() in s.lower()), "")
                                
                                if relevant_sentence:
                                    continuity.append({
                                        "content": f"Continuity reference from {line.get('character')} in episode '{episode.get('title')}': {relevant_sentence.strip()}",
                                        "metadata": {
                                            "type": "dialogue_reference",
                                            "character": line.get("character"),
                                            "episode_title": episode.get("title"),
                                            "episode_number": episode.get("episode_number"),
                                            "scene_number": scene.get("scene_number", 0)
                                        }
                                    })
        
        return continuity
    
    def _extract_relationships(self, episode: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract relationship developments from an episode.
        
        Args:
            episode: Episode data
        
        Returns:
            List of relationship memory entries
        """
        relationships = []
        
        # Extract from script interactions
        if episode.get("script") and episode["script"].get("scenes"):
            # Track character interactions by scene
            scene_interactions = {}
            
            for scene in episode["script"]["scenes"]:
                scene_number = scene.get("scene_number", 0)
                scene_interactions[scene_number] = {}
                
                # Track speaking characters
                speaking_chars = set()
                
                for line in scene.get("lines", []):
                    if line.get("type") == "dialogue":
                        char_name = line.get("character")
                        speaking_chars.add(char_name)
                        
                        # Analyze dialogue for relationship indicators
                        content = line.get("content", "")
                        
                        # Check if addressing another character
                        for other_char in speaking_chars:
                            if other_char != char_name and other_char in content:
                                # Store the interaction
                                pair_key = tuple(sorted([char_name, other_char]))
                                if pair_key not in scene_interactions[scene_number]:
                                    scene_interactions[scene_number][pair_key] = []
                                
                                scene_interactions[scene_number][pair_key].append(content)
            
            # Generate relationship memories from interactions
            for scene_number, interactions in scene_interactions.items():
                for (char1, char2), dialogues in interactions.items():
                    # Only consider substantial interactions
                    if len(dialogues) >= 2:
                        relationships.append({
                            "content": f"Relationship between {char1} and {char2} in episode '{episode.get('title')}': They interact in scene {scene_number} with dialogue including: '{dialogues[0][:100]}...'",
                            "metadata": {
                                "characters": [char1, char2],
                                "episode_title": episode.get("title"),
                                "episode_number": episode.get("episode_number"),
                                "scene_number": scene_number
                            }
                        })
        
        return relationships
    
    def add_memory(self, content: str, category: str, episode_id: str, 
                  metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add an episode memory entry.
        
        Args:
            content: Text content for the memory
            category: Category of memory (plot_point, character_development, etc.)
            episode_id: ID of the related episode
            metadata: Additional metadata
        
        Returns:
            Result of the memory addition
        """
        if not metadata:
            metadata = {}
        
        # Add required fields to metadata
        metadata.update({
            "category": category,
            "episode_id": episode_id,
            "created_at": time.time()
        })
        
        # Add to memory
        return self.mem0_client.add_episode_memory(
            content=content,
            episode_id=episode_id,
            metadata=metadata
        )
    
    def search_memories(self, query: str, category: Optional[str] = None, 
                       episode_id: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search episode memories for relevant information.
        
        Args:
            query: Search query
            category: Optional memory category to filter by
            episode_id: Optional episode ID to filter by
            limit: Maximum number of results to return
        
        Returns:
            List of matching memory entries
        """
        memories = self.mem0_client.search_episode_memories(
            query=query,
            episode_id=episode_id,
            limit=limit
        )
        
        # Filter by category if specified
        if category and memories:
            memories = [m for m in memories 
                       if m.get('metadata', {}).get('category') == category]
        
        return memories
    
    def get_all_memories(self, episode_id: Optional[str] = None, 
                        category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all episode memories, optionally filtered.
        
        Args:
            episode_id: Optional episode ID to filter by
            category: Optional memory category to filter by
        
        Returns:
            List of memory entries
        """
        # Get all episode memories
        memories = self.mem0_client.get_all_memories(
            user_id="episodes",
            memory_type=self.mem0_client.EPISODE_MEMORY
        )
        
        # Filter by episode ID if specified
        if episode_id:
            memories = [m for m in memories 
                       if m.get('metadata', {}).get('episode_id') == episode_id]
        
        # Filter by category if specified
        if category:
            memories = [m for m in memories 
                       if m.get('metadata', {}).get('category') == category]
        
        return memories
    
    def get_character_memories(self, character_name: str) -> List[Dict[str, Any]]:
        """Get all memories related to a specific character.
        
        Args:
            character_name: Name of the character
        
        Returns:
            List of memory entries about the character
        """
        # Search for character-specific memories
        memories = self.mem0_client.search_episode_memories(
            query=character_name,
            limit=50  # Get a large number of results
        )
        
        # Filter to only include memories explicitly about this character
        filtered_memories = []
        for memory in memories:
            metadata = memory.get('metadata', {})
            
            # Include character development memories for this character
            if (metadata.get('category') == self.CHARACTER_DEVELOPMENT and 
                metadata.get('character') == character_name):
                filtered_memories.append(memory)
            
            # Include relationship memories involving this character
            elif (metadata.get('category') == self.RELATIONSHIP and 
                 character_name in metadata.get('characters', [])):
                filtered_memories.append(memory)
            
            # For other memory types, check if the character is mentioned prominently
            elif (character_name.lower() in memory.get('memory', '').lower() and
                 re.search(r'\b' + re.escape(character_name) + r'\b', 
                          memory.get('memory', ''), re.IGNORECASE)):
                filtered_memories.append(memory)
        
        return filtered_memories
    
    def get_timeline(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get a chronological timeline of key events.
        
        Returns:
            Dictionary of episode IDs mapped to key plot points
        """
        # Get all continuity and plot point memories
        continuity_memories = self.get_all_memories(category=self.CONTINUITY)
        plot_memories = self.get_all_memories(category=self.PLOT_POINT)
        
        # Organize by episode
        timeline = {}
        
        for memory in continuity_memories + plot_memories:
            metadata = memory.get('metadata', {})
            episode_id = metadata.get('episode_id')
            
            if not episode_id:
                continue
            
            if episode_id not in timeline:
                timeline[episode_id] = []
            
            # Extract key information
            episode_title = metadata.get('episode_title', 'Unknown Episode')
            episode_number = metadata.get('episode_number', 0)
            
            # Add to timeline with sorting metadata
            timeline[episode_id].append({
                "memory_id": memory.get('id'),
                "content": memory.get('memory', ''),
                "category": metadata.get('category'),
                "episode_title": episode_title,
                "episode_number": episode_number,
                "scene_number": metadata.get('scene_number', 0) if 'scene_number' in metadata else 0,
                "type": metadata.get('type', 'general')
            })
        
        # Sort each episode's events by scene number
        for episode_id in timeline:
            timeline[episode_id].sort(key=lambda x: (x.get('scene_number', 0), x.get('memory_id', '')))
        
        return timeline

# Singleton instance
_episode_memory = None

def get_episode_memory() -> EpisodeMemory:
    """Get the EpisodeMemory singleton instance."""
    global _episode_memory
    
    if _episode_memory is None:
        _episode_memory = EpisodeMemory()
    
    return _episode_memory

def extract_memories(episode_id: str) -> Dict[str, List[Dict[str, Any]]]:
    """Extract and store memories from an episode.
    
    Args:
        episode_id: ID of the episode
    
    Returns:
        Dictionary of memory entries by category
    """
    memory_manager = get_episode_memory()
    return memory_manager.extract_memories_from_episode(episode_id)

def add_memory(content: str, category: str, episode_id: str,
              metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Add an episode memory entry.
    
    Args:
        content: Text content for the memory
        category: Category of memory
        episode_id: ID of the related episode
        metadata: Additional metadata
    
    Returns:
        Result of the memory addition
    """
    memory_manager = get_episode_memory()
    return memory_manager.add_memory(content, category, episode_id, metadata)

def search_memories(query: str, category: Optional[str] = None,
                  episode_id: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
    """Search episode memories.
    
    Args:
        query: Search query
        category: Optional memory category to filter by
        episode_id: Optional episode ID to filter by
        limit: Maximum number of results to return
    
    Returns:
        List of matching memory entries
    """
    memory_manager = get_episode_memory()
    return memory_manager.search_memories(query, category, episode_id, limit)

def get_timeline() -> Dict[str, List[Dict[str, Any]]]:
    """Get a chronological timeline of key events.
    
    Returns:
        Dictionary of episode IDs mapped to key plot points
    """
    memory_manager = get_episode_memory()
    return memory_manager.get_timeline()

def get_character_history(character_name: str) -> List[Dict[str, Any]]:
    """Get the development history of a character.
    
    Args:
        character_name: Name of the character
    
    Returns:
        List of memory entries about the character
    """
    memory_manager = get_episode_memory()
    return memory_manager.get_character_memories(character_name)