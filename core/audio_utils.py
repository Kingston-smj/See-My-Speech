"""
Audio utility functions for loading and converting audio files
"""

import os
import tempfile
from pathlib import Path
from typing import Optional
from pydub import AudioSegment


def load_audio_file(file_path: str) -> Optional[str]:
    """
    Load and convert audio file to a format compatible with Whisper.
    Returns the path to the converted file, or None if conversion fails.
    """
    if not os.path.exists(file_path):
        return None
    
    try:
        # Check if file is already in a supported format
        ext = Path(file_path).suffix.lower()
        supported_formats = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
        
        if ext in supported_formats:
            # For most formats, Whisper can handle them directly
            # But we might need to convert some formats
            if ext in ['.m4a', '.webm']:
                # Convert to wav for better compatibility
                audio = AudioSegment.from_file(file_path)
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                audio.export(temp_file.name, format='wav')
                return temp_file.name
            return file_path
        else:
            # Try to convert unknown formats
            audio = AudioSegment.from_file(file_path)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            audio.export(temp_file.name, format='wav')
            return temp_file.name
    except Exception as e:
        print(f"Error loading audio file: {e}")
        return None


def get_audio_info(file_path: str) -> dict:
    """
    Get information about an audio file.
    Returns a dictionary with file size, duration, format, etc.
    """
    info = {
        'file_path': file_path,
        'file_name': os.path.basename(file_path),
        'file_size': 0,
        'exists': False
    }
    
    if os.path.exists(file_path):
        info['exists'] = True
        info['file_size'] = os.path.getsize(file_path)
        
        try:
            audio = AudioSegment.from_file(file_path)
            info['duration'] = len(audio) / 1000.0  # Duration in seconds
            info['format'] = Path(file_path).suffix.lower()
        except Exception:
            info['duration'] = None
            info['format'] = None
    
    return info
