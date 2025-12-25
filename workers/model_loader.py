"""
Worker thread for loading Whisper models
"""

import whisper
from PyQt5.QtCore import QThread, pyqtSignal


class ModelLoader(QThread):
    """Worker thread for loading Whisper models"""

    progress = pyqtSignal(str)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, model_size, device):
        super().__init__()
        self.model_size = model_size
        self.device = device

    def run(self):
        """Load model in background"""
        try:
            self.progress.emit(f"Loading {self.model_size} model...")
            self.progress.emit("First time will download model, please wait...")

            model = whisper.load_model(self.model_size, device=self.device)

            self.progress.emit("Model loaded successfully!")
            self.finished.emit(model)

        except Exception as e:
            self.error.emit(f"Failed to load model: {str(e)}")
