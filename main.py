#!/usr/bin/env python
"""
Stardock Podium - AI Star Trek Podcast Generator

This module serves as the main entry point for the Stardock Podium system. It performs
environment checks, initializes all required components, and launches the CLI interface.

The system is designed to run natively on Windows 10 without requiring Docker or WSL,
while providing a complete pipeline for generating Star Trek-style podcast episodes
from reference materials.
"""

from dotenv import load_dotenv
load_dotenv()

import os
import sys
import platform
import logging
import importlib.util
import subprocess
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("stardock_podium.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Required modules
REQUIRED_MODULES = [
    ('mem0', 'Mem0 Vector Database Client'),
    ('ebooklib', 'EPUB Processing Library'),
    ('elevenlabs', 'ElevenLabs Voice Synthesis API'),
    ('openai', 'OpenAI API Client'),
    ('nltk', 'Natural Language Toolkit'),
    ('ffmpeg', 'FFmpeg Python Bindings')
]

def check_environment():
    """
    Check if the environment is suitable for running the application.
    Returns True if all checks pass, False otherwise.
    """
    checks_passed = True
    
    # Check platform
    logger.info(f"Detected platform: {platform.system()} {platform.release()}")
    if platform.system() != "Windows":
        logger.warning("This application is optimized for Windows 10. Some features may not work as expected.")
    
    # Check Python version
    python_version = sys.version_info
    logger.info(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        logger.error("Python 3.8+ is required to run this application.")
        checks_passed = False
    
    # Check required modules
    for module_name, module_desc in REQUIRED_MODULES:
        if importlib.util.find_spec(module_name) is None:
            logger.error(f"Required module not found: {module_name} ({module_desc})")
            checks_passed = False
        else:
            logger.info(f"Module found: {module_name}")
    
    # Check FFmpeg availability
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            ffmpeg_version = result.stdout.split('\n')[0]
            logger.info(f"FFmpeg found: {ffmpeg_version}")
        else:
            logger.error("FFmpeg executable not found or not working properly.")
            checks_passed = False
    except FileNotFoundError:
        logger.error("FFmpeg executable not found in PATH. Please install FFmpeg.")
        checks_passed = False
    
    # Check for API keys in environment variables
    api_keys = {
        'OPENAI_API_KEY': 'OpenAI API',
        'OPENROUTER_API_KEY': 'OpenRouter API',
        'ELEVENLABS_API_KEY': 'ElevenLabs API',
        'MEM0_API_KEY': 'Mem0 API'
    }
    
    for env_var, service_name in api_keys.items():
        if not os.getenv(env_var):
            logger.warning(f"Environment variable {env_var} for {service_name} not found.")
    
    return checks_passed

def create_default_directories():
    """Create all necessary directories for the application."""
    directories = [
        "books",      # For storing ingested books
        "analysis",   # For storing analysis results
        "episodes",   # For storing episode data
        "audio",      # For storing generated audio
        "voices",     # For voice registry data
        "temp",       # For temporary files
        "data",       # For application data
        "logs"        # For log files
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.debug(f"Created directory: {directory}")

def check_nltk_data():
    """Ensure required NLTK data is downloaded."""
    try:
        import nltk
        required_packages = ['punkt', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words']
        
        for package in required_packages:
            try:
                nltk.data.find(f'tokenizers/{package}')
                logger.debug(f"NLTK package found: {package}")
            except LookupError:
                logger.info(f"Downloading NLTK package: {package}")
                nltk.download(package, quiet=True)
    except ImportError:
        logger.error("NLTK not installed. Skipping NLTK data check.")

def display_welcome_message():
    """Display the welcome message with proper encoding."""
    # Set console encoding to UTF-8
    import sys
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    
    welcome_text = """
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                                                                            ║
    ║  ███████╗████████╗ █████╗ ██████╗ ██████╗  ██████╗  ██████╗ ██╗          ║
    ║  ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██╔═══██╗██╔═══██╗██║          ║
    ║  ███████╗   ██║   ███████║██║  ██║██║  ██║██║   ██║██║   ██║██║          ║
    ║  ╚════██║   ██║   ██╔══██║██║  ██║██║  ██║██║   ██║██║   ██║██║          ║
    ║  ███████║   ██║   ██║  ██║██████╔╝██████╔╝╚██████╔╝╚██████╔╝███████╗     ║
    ║  ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═════╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝     ║
    ║                                                                            ║
    ║  ██████╗  ██████╗ ██████╗ ██╗██╗   ██╗███╗   ███╗                        ║
    ║  ██╔══██╗██╔═══██╗██╔══██╗██║██║   ██║████╗ ████║                        ║
    ║  ██████╔╝██║   ██║██║  ██║██║██║   ██║██╔████╔██║                        ║
    ║  ██╔═══╝ ██║   ██║██║  ██║██║██║   ██║██║╚██╔╝██║                        ║
    ║  ██║     ╚██████╔╝██████╔╝██║╚██████╔╝██║ ╚═╝ ██║                        ║
    ║  ╚═╝      ╚═════╝ ╚═════╝ ╚═╝ ╚═════╝ ╚═╝     ╚═╝                        ║
    ║                                                                            ║
    ║  Welcome to Stardock Podium - Your AI-Powered Star Trek Podcast Generator   ║
    ║                                                                            ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    """
    print(welcome_text)

def init_modules():
    """Initialize required modules and verify they're working."""
    try:
        # Import and initialize modules
        from mem0_client import Mem0Client
        from epub_processor import EPUBProcessor
        from voice_registry import VoiceRegistry
        
        # Test mem0 connection
        mem0 = Mem0Client()
        
        # Initialize voice registry
        voice_registry = VoiceRegistry()
        voice_count = len(voice_registry.list_voices())
        logger.info(f"Voice registry initialized with {voice_count} voices")
        
        return True
    except Exception as e:
        logger.exception(f"Error initializing modules: {e}")
        return False

def main():
    """Main entry point for the application."""
    # Display welcome message
    display_welcome_message()
    
    # Check environment
    logger.info("Checking environment...")
    if not check_environment():
        logger.error("Environment check failed. Please fix the issues and try again.")
        return 1
    
    # Create directories
    logger.info("Creating necessary directories...")
    create_default_directories()
    
    # Check NLTK data
    logger.info("Checking NLTK data...")
    check_nltk_data()
    
    # Initialize modules
    logger.info("Initializing modules...")
    if not init_modules():
        logger.warning("Some modules failed to initialize. Functionality may be limited.")
    
    # Import CLI entrypoint and run it
    try:
        from cli_entrypoint import main as cli_main
        logger.info("Starting CLI...")
        return cli_main()
    except Exception as e:
        logger.exception(f"Error executing CLI: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())