"""
Worker thread for audio transcription
"""

import os
from PyQt5.QtCore import QThread, pyqtSignal


class TranscriptionWorker(QThread):
    """Worker thread for audio transcription"""

    progress = pyqtSignal(str)  # Progress message
    finished = pyqtSignal(dict)  # Results
    error = pyqtSignal(str)     # Error message

    def __init__(self, model, audio_file, settings):
        super().__init__()
        self.model = model
        self.audio_file = audio_file
        self.settings = settings
        self.is_cancelled = False

    def run(self):
        """Run transcription in background"""
        try:
            if not os.path.exists(self.audio_file):
                self.error.emit("Audio file not found")
                return

            if self.model is None:
                self.error.emit("Model not loaded")
                return

            self.progress.emit("Starting transcription...")

            # Get file info
            file_size = os.path.getsize(self.audio_file) / (1024 * 1024)
            self.progress.emit(f"Processing file ({file_size:.1f} MB)...")

            # Transcribe
            result = self.model.transcribe(
                self.audio_file,
                verbose=False,
                language=None if self.settings['auto_detect'] else self.settings['language'],
                task="transcribe" if not self.settings['translate'] else "translate"
            )

            if self.is_cancelled:
                return

            # Format results
            output = {
                "text": result["text"].strip(),
                "language": result["language"],
                "segments": result["segments"],
                "file_path": self.audio_file,
                "file_name": os.path.basename(self.audio_file)
            }

            self.progress.emit("Transcription complete!")
            self.finished.emit(output)

        except Exception as e:
            self.error.emit(f"Transcription failed: {str(e)}")

    def cancel(self):
        """Cancel transcription"""
        self.is_cancelled = True
