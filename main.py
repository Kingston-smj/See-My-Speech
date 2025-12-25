#!/usr/bin/env python3
"""
Whisper Audio Transcription - Qt Desktop Application
Cross-platform desktop app for local audio transcription
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import AudioTranscriptionApp


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("See My Speech")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("AudioTranscription")

    # Create and show main window
    window = AudioTranscriptionApp()
    window.show()

    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
