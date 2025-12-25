"""
History management for transcription results
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional


class HistoryManager:
    """Manages transcription history storage and retrieval"""

    def __init__(self, history_file: Optional[str] = None):
        """
        Initialize history manager.
        
        Args:
            history_file: Path to JSON file for persistent storage.
                         If None, uses default location in user's data directory.
        """
        if history_file is None:
            # Use default location in user's home directory
            home = Path.home()
            data_dir = home / '.see_my_speech'
            data_dir.mkdir(exist_ok=True)
            history_file = str(data_dir / 'transcription_history.json')
        
        self.history_file = history_file
        self.history: List[Dict[str, Any]] = []
        self.load_history()

    def load_history(self):
        """Load history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception as e:
                print(f"Error loading history: {e}")
                self.history = []

    def save_history(self):
        """Save history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")

    def add_transcription(self, result: Dict[str, Any]):
        """
        Add a transcription result to history.
        
        Args:
            result: Dictionary containing transcription results with keys:
                   - text: Transcribed text
                   - language: Detected language
                   - file_path: Path to source audio file
                   - file_name: Name of source audio file
                   - segments: (optional) Transcription segments
        """
        # Add timestamp
        result['timestamp'] = time.time()
        result['date'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        self.history.append(result)
        self.save_history()

    def get_history(self) -> List[Dict[str, Any]]:
        """Get all transcription history"""
        return self.history.copy()

    def clear_history(self):
        """Clear all transcription history"""
        self.history.clear()
        self.save_history()

    def remove_item(self, index: int):
        """Remove a specific item from history by index"""
        if 0 <= index < len(self.history):
            self.history.pop(index)
            self.save_history()

    def export_item(self, index: int, output_path: str) -> bool:
        """
        Export a history item to a text file.
        
        Args:
            index: Index of history item to export
            output_path: Path where to save the exported file
            
        Returns:
            True if export was successful, False otherwise
        """
        if not (0 <= index < len(self.history)):
            return False
        
        try:
            result = self.history[index]
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"File: {result.get('file_name', 'Unknown')}\n")
                f.write(f"Language: {result.get('language', 'Unknown')}\n")
                f.write(f"Date: {result.get('date', 'Unknown')}\n")
                if 'file_path' in result:
                    f.write(f"Path: {result['file_path']}\n")
                f.write("\nTranscription:\n")
                f.write(result.get('text', ''))
            
            return True
        except Exception as e:
            print(f"Error exporting history item: {e}")
            return False
