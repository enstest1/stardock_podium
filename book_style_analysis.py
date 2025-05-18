#!/usr/bin/env python
"""
Book Style Analysis Module for Stardock Podium.

This module analyzes the style and content of ingested books to extract
writing patterns, character archetypes, dialogue styles, and thematic elements.
The results are used to guide the podcast's storytelling style and content.
"""

import os
import json
import logging
import time
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from collections import Counter, defaultdict
import random
import string
import math

# Try to import required libraries
try:
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    import nltk
    
    # Ensure necessary NLTK data is available
    for resource in ['punkt', 'stopwords']:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except LookupError:
            nltk.download(resource, quiet=True)
except ImportError:
    logging.error("NLTK not found. Please install it with: pip install nltk")
    raise

# Local imports
from epub_processor import get_processor, get_book_content

# Setup logging
logger = logging.getLogger(__name__)

class BookStyleAnalyzer:
    """Analyzer for book style and content to extract patterns and insights."""
    
    def __init__(self, analysis_dir: str = "analysis"):
        """Initialize the book style analyzer.
        
        Args:
            analysis_dir: Directory to store analysis results
        """
        self.analysis_dir = Path(analysis_dir)
        self.analysis_dir.mkdir(exist_ok=True)
        
        # Get EPUB processor
        self.epub_processor = get_processor()
        
        # Load stopwords for analysis
        self.stopwords = set(stopwords.words('english'))
        
        # Define patterns
        self.dialogue_pattern = re.compile(r'"([^"]*)"')
        self.thought_pattern = re.compile(r'\'([^\']*)\'')
        self.sentence_end_pattern = re.compile(r'[.!?][\s")]')
    
    def analyze_book_style(self, book_id: str, deep: bool = False) -> Dict[str, Any]:
        """Analyze the style and content of a book.
        
        Args:
            book_id: ID of the book to analyze
            deep: Whether to perform a deep analysis
        
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Starting style analysis for book {book_id}")
        
        # Check if analysis already exists
        analysis_file = self.analysis_dir / f"{book_id}_style_analysis.json"
        if analysis_file.exists() and not deep:
            try:
                with open(analysis_file, 'r') as f:
                    existing_analysis = json.load(f)
                    logger.info(f"Loaded existing analysis for book {book_id}")
                    return existing_analysis
            except Exception as e:
                logger.error(f"Error loading existing analysis: {e}")
        
        # Get book content
        book_content = get_book_content(book_id)
        
        if not book_content or not book_content.get('metadata'):
            logger.error(f"Book content not found for ID: {book_id}")
            return {}
        
        # Extract metadata
        metadata = book_content['metadata']
        title = metadata.get('title', 'Unknown')
        author = metadata.get('creator', 'Unknown')
        
        logger.info(f"Analyzing book: '{title}' by {author}")
        
        # Initialize analysis result structure
        analysis = {
            "book_id": book_id,
            "title": title,
            "author": author,
            "analyzed_at": time.time(),
            "deep_analysis": deep,
            "statistics": {},
            "style": {},
            "dialogue": {},
            "characters": {},
            "themes": {},
            "settings": {},
            "plot_elements": {},
            "unique_words": {}
        }
        
        # Extract content samples
        sections = book_content.get('sections', {}).get('sections', [])
        if not sections:
            logger.error(f"No sections found for book {book_id}")
            return {}
        
        # For basic analysis, sample the sections
        if not deep:
            sections = self._sample_sections(sections)
        
        # Process the text
        text_samples = [section.get('content', '') for section in sections]
        combined_text = "\n\n".join(text_samples)
        
        # Basic text statistics
        analysis["statistics"] = self._compute_text_statistics(combined_text)
        
        # Style analysis
        analysis["style"] = self._analyze_writing_style(combined_text)
        
        # Dialogue analysis
        analysis["dialogue"] = self._analyze_dialogue(combined_text)
        
        # Character analysis
        analysis["characters"] = self._identify_characters(combined_text, book_id)
        
        # Theme analysis
        analysis["themes"] = self._identify_themes(combined_text)
        
        # Setting analysis
        analysis["settings"] = self._identify_settings(combined_text)
        
        # Plot elements
        analysis["plot_elements"] = self._identify_plot_elements(combined_text)
        
        # Vocabulary analysis
        analysis["unique_words"] = self._analyze_vocabulary(combined_text)
        
        # If deep analysis, add additional in-depth insights
        if deep:
            logger.info(f"Performing deep analysis for book {book_id}")
            
            # Add deep analysis results
            analysis["deep_insights"] = self._perform_deep_analysis(combined_text)
            
            # Add relationship analysis
            analysis["relationships"] = self._analyze_relationships(combined_text, analysis["characters"])
            
            # Add narrative arc analysis
            analysis["narrative_arc"] = self._analyze_narrative_arc(book_content)
        
        # Save analysis
        try:
            with open(analysis_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            logger.info(f"Saved analysis to {analysis_file}")
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
        
        return analysis
    
    def _sample_sections(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sample sections for analysis to reduce processing time.
        
        Args:
            sections: List of all sections
        
        Returns:
            List of sampled sections
        """
        num_sections = len(sections)
        
        if num_sections <= 10:
            # For small books, use all sections
            return sections
        elif num_sections <= 30:
            # For medium books, sample beginning, middle, and end
            indices = list(range(0, 3))
            indices.extend(range(num_sections // 2 - 1, num_sections // 2 + 2))
            indices.extend(range(num_sections - 3, num_sections))
        else:
            # For large books, sample proportionally
            indices = [0, 1, 2]  # Start
            indices.extend(random.sample(range(3, num_sections // 3), 3))  # Early
            indices.extend(random.sample(range(num_sections // 3, 2 * num_sections // 3), 4))  # Middle
            indices.extend(random.sample(range(2 * num_sections // 3, num_sections - 3), 3))  # Late
            indices.extend([num_sections - 3, num_sections - 2, num_sections - 1])  # End
        
        # Get unique sorted indices within range
        unique_indices = sorted(set(i for i in indices if 0 <= i < num_sections))
        
        return [sections[i] for i in unique_indices]
    
    def _compute_text_statistics(self, text: str) -> Dict[str, Any]:
        """Compute basic text statistics.
        
        Args:
            text: The text to analyze
        
        Returns:
            Dictionary with text statistics
        """
        statistics = {}
        
        # Tokenize
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        # Filter out punctuation from words
        words = [word for word in words if word.isalnum()]
        
        # Compute basic statistics
        statistics["total_words"] = len(words)
        statistics["total_sentences"] = len(sentences)
        statistics["unique_words"] = len(set(words))
        statistics["lexical_diversity"] = len(set(words)) / len(words) if words else 0
        
        # Compute sentence length statistics
        sentence_lengths = [len(word_tokenize(sentence)) for sentence in sentences]
        statistics["avg_sentence_length"] = sum(sentence_lengths) / len(sentences) if sentences else 0
        statistics["min_sentence_length"] = min(sentence_lengths) if sentences else 0
        statistics["max_sentence_length"] = max(sentence_lengths) if sentences else 0
        
        # Compute word length statistics
        word_lengths = [len(word) for word in words]
        statistics["avg_word_length"] = sum(word_lengths) / len(words) if words else 0
        
        # Count paragraphs
        paragraphs = re.split(r'\n{2,}', text)
        statistics["total_paragraphs"] = len(paragraphs)
        
        # Estimate reading time (words per minute)
        statistics["estimated_reading_time_mins"] = len(words) / 250
        
        return statistics
    
    def _analyze_writing_style(self, text: str) -> Dict[str, Any]:
        """Analyze the writing style of the text.
        
        Args:
            text: The text to analyze
        
        Returns:
            Dictionary with writing style analysis
        """
        style = {}
        
        # Tokenize
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        # Analyze sentence structure
        sentence_lengths = [len(word_tokenize(sentence)) for sentence in sentences]
        sentence_length_variance = sum((length - sum(sentence_lengths) / len(sentences)) ** 2 
                                   for length in sentence_lengths) / len(sentences)
        
        style["sentence_variety"] = math.sqrt(sentence_length_variance)
        
        # Calculate sentence types
        statement_count = len(re.findall(r'[.]\s', text))
        question_count = len(re.findall(r'[?]\s', text))
        exclamation_count = len(re.findall(r'[!]\s', text))
        
        total_sentence_counts = statement_count + question_count + exclamation_count
        if total_sentence_counts > 0:
            style["statement_ratio"] = statement_count / total_sentence_counts
            style["question_ratio"] = question_count / total_sentence_counts
            style["exclamation_ratio"] = exclamation_count / total_sentence_counts
        
        # Analyze paragraph structure
        paragraphs = re.split(r'\n{2,}', text)
        paragraph_lengths = [len(word_tokenize(paragraph)) for paragraph in paragraphs]
        style["avg_paragraph_length"] = sum(paragraph_lengths) / len(paragraphs) if paragraphs else 0
        
        # Identify adjective usage
        # Simple approximation - exact part-of-speech tagging would be better
        adjective_endings = ['able', 'al', 'ary', 'ent', 'ful', 'ic', 'ical', 'ish', 'less', 'ous']
        adjective_candidates = [word.lower() for word in words if any(word.lower().endswith(ending) for ending in adjective_endings)]
        style["estimated_adjective_ratio"] = len(adjective_candidates) / len(words) if words else 0
        
        # Identify adverb usage
        adverb_candidates = [word.lower() for word in words if word.lower().endswith('ly')]
        style["estimated_adverb_ratio"] = len(adverb_candidates) / len(words) if words else 0
        
        # Analyze voice (active vs. passive)
        # Simple approximation - passive voice often uses "was/were" + past participle
        passive_indicators = ['was', 'were', 'been', 'being', 'be']
        passive_constructs = sum(1 for word in words if word.lower() in passive_indicators)
        style["passive_voice_indicator"] = passive_constructs / len(sentences) if sentences else 0
        
        # Analyze narrative style (estimated 1st vs 3rd person)
        first_person_indicators = ['i', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours']
        third_person_indicators = ['he', 'she', 'it', 'they', 'him', 'her', 'them', 'his', 'hers', 'their']
        
        first_person_count = sum(1 for word in words if word.lower() in first_person_indicators)
        third_person_count = sum(1 for word in words if word.lower() in third_person_indicators)
        
        # Calculate total indicator count and narratives ratios
        total_indicators = first_person_count + third_person_count
        if total_indicators > 0:
            style["first_person_ratio"] = first_person_count / total_indicators
            style["third_person_ratio"] = third_person_count / total_indicators
            
            # Determine narrative style
            if style["first_person_ratio"] > 0.6:
                style["primary_narrative_style"] = "first_person"
            elif style["third_person_ratio"] > 0.6:
                style["primary_narrative_style"] = "third_person"
            else:
                style["primary_narrative_style"] = "mixed"
        
        # Analyze dialogue density
        dialogue_matches = re.findall(self.dialogue_pattern, text)
        style["dialogue_density"] = len(dialogue_matches) / len(sentences) if sentences else 0
        
        # Analyze descriptive vs. action-oriented content
        # Action words typically feature more verbs
        # This is a rough approximation
        action_verbs = ['run', 'jump', 'move', 'turn', 'walk', 'hit', 'grab', 'take',
                       'push', 'pull', 'throw', 'catch', 'drop', 'lift', 'fight',
                       'attack', 'defend', 'escape', 'chase', 'flee', 'shoot', 'kick']
        
        action_verb_count = sum(1 for word in words if word.lower() in action_verbs)
        style["action_verb_density"] = action_verb_count / len(words) if words else 0
        
        if style["action_verb_density"] > 0.02:
            style["content_type_inference"] = "action_oriented"
        elif style["estimated_adjective_ratio"] > 0.1:
            style["content_type_inference"] = "descriptive"
        else:
            style["content_type_inference"] = "balanced"
        
        return style
    
    def _analyze_dialogue(self, text: str) -> Dict[str, Any]:
        """Analyze dialogue patterns in the text.
        
        Args:
            text: The text to analyze
        
        Returns:
            Dictionary with dialogue analysis
        """
        dialogue = {}
        
        # Extract dialogue
        dialogue_matches = re.findall(self.dialogue_pattern, text)
        
        if not dialogue_matches:
            dialogue["total_lines"] = 0
            dialogue["present"] = False
            return dialogue
        
        dialogue["total_lines"] = len(dialogue_matches)
        dialogue["present"] = True
        
        # Analyze dialogue lines
        dialogue_lengths = [len(word_tokenize(line)) for line in dialogue_matches]
        dialogue["avg_line_length"] = sum(dialogue_lengths) / len(dialogue_lengths) if dialogue_lengths else 0
        
        # Identify question frequency in dialogue
        question_dialogues = [line for line in dialogue_matches if '?' in line]
        dialogue["question_ratio"] = len(question_dialogues) / len(dialogue_matches)
        
        # Identify exclamation frequency in dialogue
        exclamation_dialogues = [line for line in dialogue_matches if '!' in line]
        dialogue["exclamation_ratio"] = len(exclamation_dialogues) / len(dialogue_matches)
        
        # Analyze dialogue tags (if available)
        dialogue_tag_pattern = re.compile(r'"[^"]*"(?:\s+)([^,.!?;:]+)(?:ed|s)(?:\s+)')
        dialogue_tags = dialogue_tag_pattern.findall(text)
        
        # Count the most common dialogue tags
        if dialogue_tags:
            common_tags = Counter(dialogue_tags).most_common(10)
            dialogue["common_tags"] = [{"tag": tag, "count": count} for tag, count in common_tags]
        
        # Identify patterns of short vs. long exchanges
        dialogue_paragraphs = re.split(r'\n{2,}', text)
        dialogue_exchanges = [para for para in dialogue_paragraphs if '"' in para]
        
        if dialogue_exchanges:
            exchange_lengths = [para.count('"') // 2 for para in dialogue_exchanges]
            dialogue["avg_exchange_length"] = sum(exchange_lengths) / len(exchange_lengths)
            
            # Count single-line vs multi-line exchanges
            single_exchanges = sum(1 for length in exchange_lengths if length == 1)
            dialogue["single_line_ratio"] = single_exchanges / len(exchange_lengths)
        
        # Sample dialogue for style reference
        if dialogue_matches:
            # Choose some representative samples
            sample_indices = random.sample(range(len(dialogue_matches)), 
                                          min(5, len(dialogue_matches)))
            dialogue["samples"] = [dialogue_matches[i] for i in sample_indices]
        
        return dialogue
    
    def _identify_characters(self, text: str, book_id: str) -> Dict[str, Any]:
        """Identify and analyze characters in the text.
        
        Args:
            text: The text to analyze
            book_id: ID of the book
        
        Returns:
            Dictionary with character analysis
        """
        characters = {}
        
        # Check for existing character analysis
        character_file = self.analysis_dir / f"{book_id}_characters.json"
        if character_file.exists():
            try:
                with open(character_file, 'r') as f:
                    existing_analysis = json.load(f)
                    logger.info(f"Loaded existing character analysis for book {book_id}")
                    return existing_analysis
            except Exception as e:
                logger.error(f"Error loading existing character analysis: {e}")
        
        # Simple name extraction
        # This is a basic approach - more sophisticated NER would be better
        sentences = sent_tokenize(text)
        
        # Look for capitalized words that aren't at the start of sentences
        name_candidates = set()
        for sentence in sentences:
            words = word_tokenize(sentence)
            if len(words) > 1:
                for i in range(1, len(words)):
                    word = words[i]
                    # Check if capitalized and not a common stop word
                    if (word and word[0].isupper() and 
                        word.lower() not in self.stopwords and
                        len(word) > 1 and  # Exclude single letters
                        word.isalpha()):  # Only alphabetic
                        name_candidates.add(word)
        
        # Try to identify main characters by frequency
        words = word_tokenize(text)
        # Exclude words at beginning of sentences
        words = [words[i] for i in range(len(words)) if i > 0 and words[i-1] in ['.', '!', '?']]
        
        # Count name occurrences
        name_counts = Counter(word for word in words if word in name_candidates)
        
        # Get the most common names
        most_common_names = name_counts.most_common(10)
        
        # Extract character mentions with surrounding context
        character_mentions = {}
        for name, _ in most_common_names:
            mentions = []
            for sentence in sentences:
                if re.search(r'\b' + re.escape(name) + r'\b', sentence):
                    mentions.append(sentence)
            
            # Only keep a sample of mentions
            if mentions:
                character_mentions[name] = random.sample(mentions, min(5, len(mentions)))
        
        # Create character profiles
        character_profiles = []
        for name, count in most_common_names:
            if count >= 3:  # Only include characters mentioned multiple times
                profile = {
                    "name": name,
                    "mention_count": count,
                    "sample_mentions": character_mentions.get(name, []),
                    "likely_importance": "high" if count > 10 else "medium" if count > 5 else "low"
                }
                character_profiles.append(profile)
        
        characters["profiles"] = character_profiles
        characters["total_characters"] = len(character_profiles)
        
        # Save character analysis
        try:
            with open(character_file, 'w') as f:
                json.dump(characters, f, indent=2)
            logger.info(f"Saved character analysis to {character_file}")
        except Exception as e:
            logger.error(f"Error saving character analysis: {e}")
        
        return characters
    
    def _identify_themes(self, text: str) -> Dict[str, Any]:
        """Identify thematic elements in the text.
        
        Args:
            text: The text to analyze
        
        Returns:
            Dictionary with theme analysis
        """
        themes = {}
        
        # Tokenize and filter out stopwords
        words = word_tokenize(text.lower())
        filtered_words = [word for word in words if word.isalpha() and word not in self.stopwords]
        
        # Count word frequencies
        word_counts = Counter(filtered_words)
        
        # Get most common words
        common_words = word_counts.most_common(100)
        
        # Define common theme categories
        theme_categories = {
            "adventure": ['journey', 'quest', 'adventure', 'discover', 'exploration', 'mission'],
            "romance": ['love', 'heart', 'romance', 'passion', 'kiss', 'embrace'],
            "conflict": ['war', 'battle', 'fight', 'conflict', 'struggle', 'confrontation'],
            "identity": ['self', 'identity', 'discover', 'true', 'become', 'change'],
            "power": ['power', 'control', 'authority', 'command', 'rule', 'dominate'],
            "justice": ['justice', 'fair', 'right', 'law', 'punishment', 'crime'],
            "family": ['family', 'father', 'mother', 'parent', 'child', 'brother', 'sister'],
            "technology": ['machine', 'computer', 'technology', 'device', 'system', 'program'],
            "nature": ['nature', 'tree', 'river', 'mountain', 'forest', 'earth', 'animal'],
            "survival": ['survive', 'escape', 'danger', 'threat', 'risk', 'death', 'alive'],
            "mystery": ['mystery', 'secret', 'hidden', 'discover', 'reveal', 'clue'],
            "leadership": ['leader', 'follow', 'command', 'direct', 'guide', 'decision'],
            "morality": ['moral', 'right', 'wrong', 'good', 'evil', 'ethical', 'choice'],
            "science": ['science', 'experiment', 'research', 'discovery', 'theory', 'laboratory'],
            "space": ['space', 'planet', 'star', 'galaxy', 'universe', 'cosmic', 'orbit']
        }
        
        # Score each theme category
        theme_scores = {}
        for category, keywords in theme_categories.items():
            score = sum(count for word, count in common_words if word in keywords)
            theme_scores[category] = score
        
        # Normalize scores
        max_score = max(theme_scores.values()) if theme_scores else 1
        normalized_scores = {category: score / max_score for category, score in theme_scores.items()}
        
        # Sort themes by score
        sorted_themes = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Identify primary and secondary themes
        themes["primary"] = [theme for theme, score in sorted_themes[:3] if score > 0.5]
        themes["secondary"] = [theme for theme, score in sorted_themes[3:6] if score > 0.3]
        themes["all_scores"] = normalized_scores
        
        # Include most common thematic words
        themes["common_thematic_words"] = [{"word": word, "count": count} 
                                          for word, count in common_words[:20]]
        
        return themes
    
    def _identify_settings(self, text: str) -> Dict[str, Any]:
        """Identify setting elements in the text.
        
        Args:
            text: The text to analyze
        
        Returns:
            Dictionary with setting analysis
        """
        settings = {}
        
        # Define setting categories and keywords
        setting_categories = {
            "urban": ['city', 'street', 'building', 'apartment', 'urban', 'downtown'],
            "rural": ['farm', 'field', 'village', 'countryside', 'rural', 'barn'],
            "futuristic": ['future', 'advanced', 'technology', 'spacecraft', 'robot', 'hologram'],
            "historical": ['ancient', 'medieval', 'century', 'historical', 'kingdom', 'empire'],
            "natural": ['forest', 'mountain', 'river', 'lake', 'ocean', 'nature', 'tree'],
            "space": ['space', 'planet', 'star', 'ship', 'station', 'orbit', 'galaxy'],
            "indoor": ['room', 'house', 'inside', 'interior', 'corridor', 'hall'],
            "underwater": ['ocean', 'underwater', 'sea', 'submarine', 'aquatic', 'marine'],
            "military": ['base', 'outpost', 'command', 'ship', 'bunker', 'fortress']
        }
        
        # Check time period indicators
        time_periods = {
            "prehistoric": ['prehistoric', 'ancient', 'primitive', 'stone age', 'dinosaur'],
            "antiquity": ['ancient', 'roman', 'greek', 'egyptian', 'babylon', 'pharaoh'],
            "medieval": ['medieval', 'castle', 'knight', 'kingdom', 'middle ages', 'sword'],
            "renaissance": ['renaissance', 'reformation', 'tudor', 'elizabethan'],
            "industrial": ['industrial', 'factory', 'steam', 'victorian', '19th century'],
            "modern": ['modern', 'contemporary', 'present day', 'current', 'today'],
            "near_future": ['near future', 'upcoming', 'soon', 'next decade', 'tomorrow'],
            "far_future": ['distant future', 'far future', 'centuries ahead', 'millennia', 'eon']
        }
        
        # Tokenize and analyze
        words = word_tokenize(text.lower())
        text_lower = text.lower()
        
        # Score settings
        setting_scores = {}
        for category, keywords in setting_categories.items():
            score = sum(words.count(keyword) for keyword in keywords)
            setting_scores[category] = score
        
        # Score time periods
        time_scores = {}
        for period, keywords in time_periods.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            time_scores[period] = score
        
        # Normalize and sort
        if setting_scores:
            max_setting = max(setting_scores.values())
            if max_setting > 0:
                normalized_settings = {k: v / max_setting for k, v in setting_scores.items()}
                sorted_settings = sorted(normalized_settings.items(), key=lambda x: x[1], reverse=True)
                settings["primary_setting"] = sorted_settings[0][0] if sorted_settings[0][1] > 0.3 else "undefined"
                settings["setting_scores"] = normalized_settings
        
        if time_scores:
            max_time = max(time_scores.values())
            if max_time > 0:
                normalized_times = {k: v / max_time for k, v in time_scores.items()}
                sorted_times = sorted(normalized_times.items(), key=lambda x: x[1], reverse=True)
                settings["time_period"] = sorted_times[0][0] if sorted_times[0][1] > 0.3 else "undefined"
                settings["time_scores"] = normalized_times
        
        # Extract location mentions
        location_indicators = ['at', 'in', 'on', 'near', 'inside', 'outside', 'across', 'beyond']
        location_candidates = []
        
        sentences = sent_tokenize(text)
        for sentence in sentences:
            words = word_tokenize(sentence)
            for i, word in enumerate(words):
                if word.lower() in location_indicators and i + 1 < len(words):
                    if words[i+1][0].isupper():  # Check for proper noun
                        # Capture 1-3 subsequent capitalized words
                        loc = []
                        for j in range(i+1, min(i+4, len(words))):
                            if words[j][0].isupper() and words[j].isalpha():
                                loc.append(words[j])
                            else:
                                break
                        if loc:
                            location_candidates.append(' '.join(loc))
        
        # Count and rank location mentions
        if location_candidates:
            location_counts = Counter(location_candidates)
            common_locations = location_counts.most_common(5)
            settings["mentioned_locations"] = [{"location": loc, "count": count} 
                                             for loc, count in common_locations if count > 1]
        
        return settings
    
    def _identify_plot_elements(self, text: str) -> Dict[str, Any]:
        """Identify potential plot elements in the text.
        
        Args:
            text: The text to analyze
        
        Returns:
            Dictionary with plot element analysis
        """
        plot_elements = {}
        
        # Define plot element categories
        plot_categories = {
            "quest": ['search', 'seek', 'find', 'quest', 'journey', 'mission'],
            "conflict": ['battle', 'fight', 'war', 'conflict', 'struggle', 'confront'],
            "mystery": ['mystery', 'secret', 'clue', 'reveal', 'discover', 'unknown'],
            "betrayal": ['betray', 'deceive', 'trick', 'treachery', 'traitor'],
            "rescue": ['save', 'rescue', 'protect', 'defend', 'help'],
            "transformation": ['change', 'transform', 'become', 'evolve', 'grow'],
            "revenge": ['revenge', 'avenge', 'vengeance', 'payback', 'retribution'],
            "discovery": ['discover', 'find', 'uncover', 'learn', 'realize'],
            "escape": ['escape', 'flee', 'run', 'evade', 'avoid', 'breakout'],
            "sacrifice": ['sacrifice', 'give up', 'surrender', 'offer', 'forfeit']
        }
        
        # Tokenize text
        words = word_tokenize(text.lower())
        text_lower = text.lower()
        
        # Score plot elements
        plot_scores = {}
        for category, keywords in plot_categories.items():
            # Check for individual words
            word_score = sum(words.count(keyword) for keyword in keywords)
            # Check for phrases (may contain multiple words)
            phrase_score = sum(text_lower.count(keyword) for keyword in keywords if ' ' in keyword)
            plot_scores[category] = word_score + phrase_score * 2  # Weight phrases higher
        
        # Normalize and sort
        if plot_scores:
            max_score = max(plot_scores.values())
            if max_score > 0:
                normalized_scores = {k: v / max_score for k, v in plot_scores.items()}
                sorted_plots = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
                
                # Extract top plot elements
                plot_elements["primary_elements"] = [plot for plot, score in sorted_plots[:3] 
                                                   if score > 0.4]
                plot_elements["element_scores"] = normalized_scores
        
        # Look for save-the-cat structure elements
        save_cat_elements = {
            "opening_image": "opening|begins|start|first",
            "theme_stated": "theme|message|moral|lesson",
            "setup": "introduce|establish|setting|background",
            "catalyst": "catalyst|event|trigger|inciting|incident",
            "debate": "debate|hesitate|doubt|question|uncertain",
            "break_into_two": "decision|choice|accept|begin journey",
            "b_story": "subplot|secondary|relationship|love interest",
            "fun_and_games": "adventure|exploration|action|discovery",
            "midpoint": "middle|halfway|midpoint|turn|twist",
            "bad_guys_close_in": "threat|danger|enemy|opponent|challenge",
            "all_is_lost": "defeat|failure|loss|despair|lowest point",
            "dark_night_of_soul": "reflection|introspection|doubt|hopeless",
            "break_into_three": "solution|realization|plan|inspiration",
            "finale": "climax|showdown|confrontation|final battle",
            "final_image": "ending|conclusion|resolution|final"
        }
        
        # Check for save-the-cat elements
        save_cat_scores = {}
        for element, patterns in save_cat_elements.items():
            # Create a regex pattern
            pattern = re.compile(r'\b(' + patterns.replace('|', '|') + r')\b', re.IGNORECASE)
            # Count matches
            matches = pattern.findall(text)
            save_cat_scores[element] = len(matches)
        
        # Normalize and include
        if save_cat_scores:
            total_matches = sum(save_cat_scores.values())
            if total_matches > 0:
                # Convert to relative proportions
                normalized_save_cat = {k: v / total_matches for k, v in save_cat_scores.items()}
                plot_elements["save_the_cat_structure"] = normalized_save_cat
        
        return plot_elements
    
    def _analyze_vocabulary(self, text: str) -> Dict[str, Any]:
        """Analyze vocabulary uniqueness and complexity.
        
        Args:
            text: The text to analyze
        
        Returns:
            Dictionary with vocabulary analysis
        """
        vocabulary = {}
        
        # Tokenize and clean
        words = word_tokenize(text.lower())
        words = [word for word in words if word.isalpha()]
        
        # Calculate frequency distribution
        word_freq = Counter(words)
        
        # Calculate common words (minus stopwords)
        content_words = [word for word in words if word not in self.stopwords]
        content_freq = Counter(content_words)
        
        # Get most common content words
        most_common = content_freq.most_common(20)
        vocabulary["common_content_words"] = [{"word": word, "count": count} for word, count in most_common]
        
        # Analyze complexity
        word_lengths = [len(word) for word in content_words]
        vocabulary["avg_content_word_length"] = sum(word_lengths) / len(word_lengths) if word_lengths else 0
        
        # Check for advanced vocabulary
        advanced_words = [word for word in content_words if len(word) > 8]
        vocabulary["advanced_word_ratio"] = len(advanced_words) / len(content_words) if content_words else 0
        
        # Sample some unique advanced words
        if advanced_words:
            unique_advanced = list(set(advanced_words))
            if len(unique_advanced) > 10:
                vocabulary["advanced_word_samples"] = random.sample(unique_advanced, 10)
            else:
                vocabulary["advanced_word_samples"] = unique_advanced
        
        return vocabulary
    
    def _perform_deep_analysis(self, text: str) -> Dict[str, Any]:
        """Perform deeper analysis for more sophisticated insights.
        
        Args:
            text: The text to analyze
        
        Returns:
            Dictionary with deep analysis results
        """
        deep_insights = {}
        
        # Analyze emotional tone
        emotion_categories = {
            "joy": ['happy', 'joy', 'delight', 'pleasure', 'thrill', 'smile', 'laugh'],
            "sadness": ['sad', 'grief', 'sorrow', 'mourn', 'depression', 'despair', 'melancholy'],
            "anger": ['angry', 'fury', 'rage', 'hate', 'outrage', 'irritation', 'frustration'],
            "fear": ['fear', 'terror', 'horror', 'dread', 'panic', 'alarm', 'shock'],
            "surprise": ['surprise', 'amazement', 'astonishment', 'wonder', 'shock'],
            "disgust": ['disgust', 'revulsion', 'loathing', 'distaste', 'aversion'],
            "anticipation": ['anticipation', 'expectation', 'prospect', 'suspense', 'tension']
        }
        
        # Score emotions
        words = word_tokenize(text.lower())
        emotion_scores = {}
        for emotion, keywords in emotion_categories.items():
            score = sum(words.count(keyword) for keyword in keywords)
            emotion_scores[emotion] = score
        
        # Normalize and sort
        if emotion_scores:
            max_score = max(emotion_scores.values())
            if max_score > 0:
                normalized_emotions = {k: v / max_score for k, v in emotion_scores.items()}
                deep_insights["emotional_tone"] = normalized_emotions
                
                # Determine primary emotions
                sorted_emotions = sorted(normalized_emotions.items(), key=lambda x: x[1], reverse=True)
                deep_insights["primary_emotions"] = [emotion for emotion, score in sorted_emotions[:2] 
                                                   if score > 0.4]
        
        # Analyze writing complexity
        syllable_pattern = re.compile(r'[aeiouy]+', re.IGNORECASE)
        sentences = sent_tokenize(text)
        word_count = len([word for word in words if word.isalpha()])
        sentence_count = len(sentences)
        
        # Calculate approximate syllables
        syllable_count = 0
        for word in words:
            if word.isalpha():
                syllables = len(syllable_pattern.findall(word))
                # Every word has at least one syllable
                syllable_count += max(1, syllables)
        
        # Calculate Flesch-Kincaid metrics
        if sentence_count > 0 and word_count > 0:
            # Flesch Reading Ease
            reading_ease = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllable_count / word_count)
            # Flesch-Kincaid Grade Level
            grade_level = 0.39 * (word_count / sentence_count) + 11.8 * (syllable_count / word_count) - 15.59
            
            deep_insights["reading_complexity"] = {
                "reading_ease": reading_ease,
                "grade_level": grade_level,
                "interpretation": self._interpret_reading_complexity(reading_ease)
            }
        
        # Analyze rhythm and pacing
        para_lengths = [len(para.split()) for para in re.split(r'\n{2,}', text)]
        if para_lengths:
            variance = sum((length - sum(para_lengths) / len(para_lengths)) ** 2 for length in para_lengths) / len(para_lengths)
            deep_insights["pacing"] = {
                "paragraph_length_variance": variance,
                "fast_paced_sections_ratio": len([l for l in para_lengths if l < 30]) / len(para_lengths),
                "interpretation": "fast_paced" if variance > 200 else "moderate_paced" if variance > 100 else "steady_paced"
            }
        
        return deep_insights
    
    def _interpret_reading_complexity(self, reading_ease: float) -> str:
        """Interpret the Flesch Reading Ease score.
        
        Args:
            reading_ease: Flesch Reading Ease score
        
        Returns:
            String interpretation of the score
        """
        if reading_ease >= 90:
            return "very_easy"
        elif reading_ease >= 80:
            return "easy"
        elif reading_ease >= 70:
            return "fairly_easy"
        elif reading_ease >= 60:
            return "standard"
        elif reading_ease >= 50:
            return "fairly_difficult"
        elif reading_ease >= 30:
            return "difficult"
        else:
            return "very_difficult"
    
    def _analyze_relationships(self, text: str, characters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze character relationships.
        
        Args:
            text: The text to analyze
            characters: The character analysis results
        
        Returns:
            Dictionary with relationship analysis
        """
        relationships = {}
        
        character_profiles = characters.get("profiles", [])
        if not character_profiles:
            return {"character_pairs": []}
        
        # Extract character names
        character_names = [profile["name"] for profile in character_profiles]
        
        # Look for co-occurrences in sentences
        sentences = sent_tokenize(text)
        
        # Create a co-occurrence matrix
        character_pairs = []
        for i, name_a in enumerate(character_names):
            for j, name_b in enumerate(character_names):
                if i < j:  # Only process unique pairs
                    # Count sentences where both characters are mentioned
                    co_occurrences = sum(1 for sentence in sentences 
                                        if re.search(r'\b' + re.escape(name_a) + r'\b', sentence) 
                                        and re.search(r'\b' + re.escape(name_b) + r'\b', sentence))
                    
                    if co_occurrences > 0:
                        character_pairs.append({
                            "character_a": name_a,
                            "character_b": name_b,
                            "co_occurrences": co_occurrences,
                            "sample_interaction": self._find_interaction_sample(sentences, name_a, name_b)
                        })
        
        # Sort by co-occurrence count
        character_pairs.sort(key=lambda x: x["co_occurrences"], reverse=True)
        
        # Take top 10 most significant relationships
        relationships["character_pairs"] = character_pairs[:10]
        
        return relationships
    
    def _find_interaction_sample(self, sentences: List[str], name_a: str, name_b: str) -> str:
        """Find a sample sentence showing interaction between characters.
        
        Args:
            sentences: List of sentences from the text
            name_a: First character name
            name_b: Second character name
        
        Returns:
            A sample sentence containing both characters
        """
        # Find sentences with both characters
        both_sentences = [sentence for sentence in sentences 
                        if re.search(r'\b' + re.escape(name_a) + r'\b', sentence) 
                        and re.search(r'\b' + re.escape(name_b) + r'\b', sentence)]
        
        # Prefer sentences with dialogue
        dialogue_sentences = [sentence for sentence in both_sentences if '"' in sentence]
        
        if dialogue_sentences:
            # Return a dialogue sentence
            return random.choice(dialogue_sentences)
        elif both_sentences:
            # Return any co-occurrence sentence
            return random.choice(both_sentences)
        else:
            return ""
    
    def _analyze_narrative_arc(self, book_content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the narrative arc of the book.
        
        Args:
            book_content: Book content dictionary
        
        Returns:
            Dictionary with narrative arc analysis
        """
        narrative_arc = {}
        
        sections = book_content.get('sections', {}).get('sections', [])
        if not sections:
            return narrative_arc
        
        num_sections = len(sections)
        
        # Divide the book into beginning, middle, and end
        beginning = sections[:num_sections // 3]
        middle = sections[num_sections // 3: 2 * num_sections // 3]
        end = sections[2 * num_sections // 3:]
        
        # Combine text for each part
        beginning_text = "\n\n".join(section.get('content', '') for section in beginning)
        middle_text = "\n\n".join(section.get('content', '') for section in middle)
        end_text = "\n\n".join(section.get('content', '') for section in end)
        
        # Analyze dialogue density across parts
        dialogue_pattern = re.compile(r'"([^"]*)"')
        beginning_dialogues = dialogue_pattern.findall(beginning_text)
        middle_dialogues = dialogue_pattern.findall(middle_text)
        end_dialogues = dialogue_pattern.findall(end_text)
        
        # Calculate dialogue density
        beginning_density = len(beginning_dialogues) / len(sent_tokenize(beginning_text)) if beginning_text else 0
        middle_density = len(middle_dialogues) / len(sent_tokenize(middle_text)) if middle_text else 0
        end_density = len(end_dialogues) / len(sent_tokenize(end_text)) if end_text else 0
        
        narrative_arc["dialogue_progression"] = {
            "beginning": beginning_density,
            "middle": middle_density,
            "end": end_density
        }
        
        # Analyze emotional tone in each part
        emotion_categories = {
            "joy": ['happy', 'joy', 'delight', 'pleasure', 'thrill', 'smile', 'laugh'],
            "sadness": ['sad', 'grief', 'sorrow', 'mourn', 'depression', 'despair', 'melancholy'],
            "anger": ['angry', 'fury', 'rage', 'hate', 'outrage', 'irritation', 'frustration'],
            "fear": ['fear', 'terror', 'horror', 'dread', 'panic', 'alarm', 'shock'],
            "tension": ['tension', 'suspense', 'anticipation', 'nervous', 'worry', 'concern', 'anxiety']
        }
        
        # Calculate emotional profiles for each part
        beginning_emotions = self._calculate_emotional_profile(beginning_text, emotion_categories)
        middle_emotions = self._calculate_emotional_profile(middle_text, emotion_categories)
        end_emotions = self._calculate_emotional_profile(end_text, emotion_categories)
        
        narrative_arc["emotional_arc"] = {
            "beginning": beginning_emotions,
            "middle": middle_emotions,
            "end": end_emotions
        }
        
        # Infer narrative structure based on emotional arcs
        narrative_arc["structure_inference"] = self._infer_narrative_structure(
            beginning_emotions, middle_emotions, end_emotions)
        
        return narrative_arc
    
    def _calculate_emotional_profile(self, text: str, 
                                    emotion_categories: Dict[str, List[str]]) -> Dict[str, float]:
        """Calculate emotional profile for a text segment.
        
        Args:
            text: The text to analyze
            emotion_categories: Dictionary of emotion categories and keywords
        
        Returns:
            Dictionary with normalized emotion scores
        """
        words = word_tokenize(text.lower())
        emotion_scores = {}
        
        for emotion, keywords in emotion_categories.items():
            score = sum(words.count(keyword) for keyword in keywords)
            emotion_scores[emotion] = score
        
        # Normalize scores
        max_score = max(emotion_scores.values()) if emotion_scores and max(emotion_scores.values()) > 0 else 1
        normalized_emotions = {k: v / max_score for k, v in emotion_scores.items()}
        
        return normalized_emotions
    
    def _infer_narrative_structure(self, beginning: Dict[str, float], 
                                 middle: Dict[str, float], 
                                 end: Dict[str, float]) -> Dict[str, Any]:
        """Infer narrative structure based on emotional arcs.
        
        Args:
            beginning: Emotional profile of the beginning
            middle: Emotional profile of the middle
            end: Emotional profile of the end
        
        Returns:
            Dictionary with narrative structure inference
        """
        # Check for common narrative patterns
        tension_growth = (middle.get('tension', 0) > beginning.get('tension', 0) and 
                         middle.get('tension', 0) > end.get('tension', 0))
        
        joy_increase = end.get('joy', 0) > beginning.get('joy', 0)
        sadness_increase = end.get('sadness', 0) > beginning.get('sadness', 0)
        
        fear_middle_spike = (middle.get('fear', 0) > beginning.get('fear', 0) and 
                           middle.get('fear', 0) > end.get('fear', 0))
        
        # Infer the likely structure
        structure = {}
        
        if tension_growth and fear_middle_spike and joy_increase:
            structure["type"] = "classic_hero_journey"
            structure["description"] = "Classic hero's journey with tension that builds, peaks, and resolves"
        
        elif tension_growth and sadness_increase:
            structure["type"] = "tragedy"
            structure["description"] = "Tragic arc with rising tension and sad conclusion"
        
        elif fear_middle_spike and joy_increase:
            structure["type"] = "challenge_and_triumph"
            structure["description"] = "Characters face challenges which they overcome successfully"
        
        elif middle.get('anger', 0) > beginning.get('anger', 0) and middle.get('anger', 0) > end.get('anger', 0):
            structure["type"] = "conflict_resolution"
            structure["description"] = "Central conflict with eventual resolution"
        
        else:
            structure["type"] = "mixed"
            structure["description"] = "Complex structure with mixed emotional patterns"
        
        return structure

# Function to analyze a book's style
def analyze_book_style(book_id: str, deep: bool = False) -> Dict[str, Any]:
    """Analyze the style and content of a book.
    
    Args:
        book_id: ID of the book to analyze
        deep: Whether to perform a deep analysis
    
    Returns:
        Dictionary with analysis results
    """
    analyzer = BookStyleAnalyzer()
    return analyzer.analyze_book_style(book_id, deep)