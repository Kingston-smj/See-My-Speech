"""
Main application window for Whisper Audio Transcription
"""

import os
import time
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QFileDialog, QProgressBar,
    QComboBox, QCheckBox, QTabWidget, QListWidget, QListWidgetItem,
    QGroupBox, QGridLayout, QMessageBox, QStatusBar
)
from PyQt5.QtCore import Qt, QSettings

from core.system_checker import SystemChecker
from workers.transcription_worker import TranscriptionWorker
from workers.model_loader import ModelLoader
from core.history_manager import HistoryManager
from ui.themes import LIGHT_THEME, DARK_THEME


class AudioTranscriptionApp(QMainWindow):
    """Main application window"""

    def apply_theme(self, theme_name):
        if theme_name == "dark":
            self.setStyleSheet(DARK_THEME)
        else:
            self.setStyleSheet(LIGHT_THEME)

        self.settings.setValue("theme", theme_name)

    def on_theme_changed(self, theme_name):
        self.apply_theme(theme_name)

    def __init__(self):
        super().__init__()
        self.model = None
        self.transcription_worker = None
        self.model_loader = None
        self.system_info = SystemChecker.check_system()
        self.transcription_history = []

        # Settings
        self.settings = QSettings('WhisperTranscription', 'TranscriptionApp')

        # History manager
        self.history_manager = HistoryManager()

        self.init_ui()
        self.load_settings()
        self.load_history()

        # Auto-load recommended model
        self.load_model(self.system_info['recommended_model'])

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Whisper Audio Transcription")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Create tabs
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Transcription tab
        self.create_transcription_tab()

        # History tab
        self.create_history_tab()

        # Settings tab
        self.create_settings_tab()

        # System info tab
        self.create_system_tab()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Update system info display after UI is created
        self.update_system_info_display()

    def create_transcription_tab(self):
        """Create main transcription tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # File input section
        file_group = QGroupBox("Audio File")
        file_layout = QVBoxLayout(file_group)

        # File selection
        file_select_layout = QHBoxLayout()
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("padding: 5px; border: 1px solid #ccc; background: #f9f9f9;")
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_file)

        file_select_layout.addWidget(self.file_path_label, 1)
        file_select_layout.addWidget(self.browse_btn)
        file_layout.addLayout(file_select_layout)

        # Quick options
        options_layout = QHBoxLayout()
        self.auto_detect_cb = QCheckBox("Auto-detect language")
        self.auto_detect_cb.setChecked(True)
        self.translate_cb = QCheckBox("Translate to English")
        self.timestamps_cb = QCheckBox("Include timestamps")
        self.timestamps_cb.setChecked(True)

        options_layout.addWidget(self.auto_detect_cb)
        options_layout.addWidget(self.translate_cb)
        options_layout.addWidget(self.timestamps_cb)
        options_layout.addStretch()

        file_layout.addLayout(options_layout)
        layout.addWidget(file_group)

        # Control buttons
        control_layout = QHBoxLayout()
        self.transcribe_btn = QPushButton("🎯 Start Transcription")
        self.transcribe_btn.setMinimumHeight(40)
        self.transcribe_btn.clicked.connect(self.start_transcription)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_transcription)

        control_layout.addWidget(self.transcribe_btn, 1)
        control_layout.addWidget(self.cancel_btn)
        layout.addLayout(control_layout)

        # Results section
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout(results_group)

        # Detected language
        self.language_label = QLabel("Language: Not detected")
        results_layout.addWidget(self.language_label)

        # Transcription text
        self.transcription_text = QTextEdit()
        self.transcription_text.setPlaceholderText("Transcription will appear here...")
        results_layout.addWidget(self.transcription_text)

        # Save buttons
        save_layout = QHBoxLayout()
        self.save_txt_btn = QPushButton("Save as TXT")
        self.save_txt_btn.clicked.connect(self.save_as_txt)
        self.save_txt_btn.setEnabled(False)

        self.copy_btn = QPushButton("Copy to Clipboard")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_btn.setEnabled(False)

        save_layout.addWidget(self.save_txt_btn)
        save_layout.addWidget(self.copy_btn)
        save_layout.addStretch()

        results_layout.addLayout(save_layout)
        layout.addWidget(results_group)

        self.tab_widget.addTab(tab, "Transcription")

    def create_history_tab(self):
        """Create transcription history tab"""
        tab = QWidget()
        layout = QHBoxLayout(tab)

        # History list
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.show_history_item)
        layout.addWidget(self.history_list, 1)

        # History details
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)

        self.history_info = QLabel("Select an item to view details")
        details_layout.addWidget(self.history_info)

        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        details_layout.addWidget(self.history_text)

        # History controls
        history_controls = QHBoxLayout()
        self.export_history_btn = QPushButton("Export Selected")
        self.export_history_btn.clicked.connect(self.export_history_item)
        self.export_history_btn.setEnabled(False)

        self.clear_history_btn = QPushButton("Clear History")
        self.clear_history_btn.clicked.connect(self.clear_history)

        history_controls.addWidget(self.export_history_btn)
        history_controls.addWidget(self.clear_history_btn)
        history_controls.addStretch()

        details_layout.addLayout(history_controls)
        layout.addWidget(details_widget, 2)

        self.tab_widget.addTab(tab, "History")

    def create_settings_tab(self):
        """Create settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Model settings
        model_group = QGroupBox("Model Settings")
        model_layout = QGridLayout(model_group)

        model_layout.addWidget(QLabel("Model Size:"), 0, 0)
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large"])
        self.model_combo.setCurrentText(self.system_info['recommended_model'])
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        model_layout.addWidget(self.model_combo, 0, 1)

        self.reload_model_btn = QPushButton("Reload Model")
        self.reload_model_btn.clicked.connect(self.reload_current_model)
        model_layout.addWidget(self.reload_model_btn, 0, 2)

        layout.addWidget(model_group)

        # Output settings
        output_group = QGroupBox("Output Settings")
        output_layout = QGridLayout(output_group)

        output_layout.addWidget(QLabel("Default Output Folder:"), 0, 0)
        self.output_folder_label = QLabel("Default (same as input)")
        output_layout.addWidget(self.output_folder_label, 0, 1)

        self.browse_output_btn = QPushButton("Browse")
        self.browse_output_btn.clicked.connect(self.browse_output_folder)
        output_layout.addWidget(self.browse_output_btn, 0, 2)

        layout.addWidget(output_group)

        # Theme settings
        theme_group = QGroupBox("Theme")
        theme_layout = QGridLayout(theme_group)

        theme_layout.addWidget(QLabel("Select Theme:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo, 0, 1)

        layout.addWidget(theme_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "Settings")

    def create_system_tab(self):
        """Create system information tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        #refrsh button
        refresh_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Refresh System Info")
        refresh_btn.setMaximumWidth(200)
        refresh_btn.clicked.connect(self.refresh_system_info)
        refresh_layout.addWidget(refresh_btn)
        refresh_layout.addStretch()
        layout.addLayout(refresh_layout)

        # System info group
        self.system_info_group = QGroupBox("System Information")
        self.system_info_layout = QVBoxLayout(self.system_info_group)

        #Create label for system info (store as instance variable so it can be updated)
        self.system_info_label = QLabel()
        self.system_info_label.setWordWrap(True)
        self.system_info_layout.addWidget(self.system_info_label)

        layout.addWidget(self.system_info_group)

        # Model info
        model_info_group = QGroupBox("Model Information")
        model_info_layout = QVBoxLayout(model_info_group)

        model_info_text = """
        <b>Model Sizes:</b><br>
        • <b>tiny</b>: ~39 MB, fastest, least accurate<br>
        • <b>base</b>: ~74 MB, good balance ⭐<br>
        • <b>small</b>: ~244 MB, better accuracy<br>
        • <b>medium</b>: ~769 MB, high accuracy<br>
        • <b>large</b>: ~1550 MB, best accuracy<br>
        """

        model_info_label = QLabel(model_info_text)
        model_info_label.setWordWrap(True)
        model_info_layout.addWidget(model_info_label)

        layout.addWidget(model_info_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "System Info")

    def update_system_info_display(self):
        """Update the system information display"""
        # Get fresh system info
        info = self.system_info

        info_text = f"""
        <b>Python Version:</b> {info['python_version']}<br>
        <b>PyTorch Version:</b> {info['torch_version']}<br>
        <b>Device:</b> {info['device'].upper()}<br>
        """

        if info['gpu_name']:
            info_text += f"<b>GPU:</b> {info['gpu_name']}<br>"
            info_text += f"<b>GPU Memory:</b> {info['gpu_memory']:.1f} GB<br>"

        info_text += f"<b>Available RAM:</b> {info['ram_available']:.1f} GB<br>"
        info_text += f"<b>Recommended Model:</b> {info['recommended_model']}"

        self.system_info_label.setText(info_text)

    def refresh_system_info(self):
        """Refresh system information"""
        self.status_bar.showMessage("Refreshing system information...")

        # Re-check system capabilities
        self.system_info = SystemChecker.check_system()

        # Update the display
        self.update_system_info_display()

        self.status_bar.showMessage("System information refreshed", 3000)

    def load_settings(self):
        """Load application settings"""
        # Load model preference
        saved_model = self.settings.value('model_size', self.system_info['recommended_model'])
        self.model_combo.setCurrentText(saved_model)

        # Load other settings
        self.auto_detect_cb.setChecked(self.settings.value('auto_detect', True, type=bool))
        self.timestamps_cb.setChecked(self.settings.value('timestamps', True, type=bool))

        # load theme
        theme = self.settings.value("theme", "light")
        self.theme_combo.setCurrentText(theme)
        self.apply_theme(theme)

    def load_history(self):
        """Load transcription history from history manager"""
        saved_history = self.history_manager.get_history()
        self.transcription_history = saved_history
        
        # Populate history list
        for idx, result in enumerate(saved_history):
            item_text = f"{result.get('file_name', 'Unknown')} - {result.get('language', 'Unknown')} - {result.get('date', 'Unknown')}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, idx)
            self.history_list.addItem(item)

    def save_settings(self):
        """Save application settings"""
        self.settings.setValue('model_size', self.model_combo.currentText())
        self.settings.setValue('auto_detect', self.auto_detect_cb.isChecked())
        self.settings.setValue('timestamps', self.timestamps_cb.isChecked())

    def browse_file(self):
        """Browse for audio file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.mp3 *.wav *.m4a *.flac *.ogg *.mp4 *.webm);;All Files (*)"
        )

        if file_path:
            self.file_path_label.setText(file_path)
            self.transcribe_btn.setEnabled(True)

    def browse_output_folder(self):
        """Browse for output folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder_label.setText(folder)
            self.settings.setValue('output_folder', folder)

    def load_model(self, model_size):
        """Load Whisper model"""
        if self.model_loader and self.model_loader.isRunning():
            return

        self.status_bar.showMessage(f"Loading {model_size} model...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate

        self.model_loader = ModelLoader(model_size, self.system_info['device'])
        self.model_loader.progress.connect(self.update_status)
        self.model_loader.finished.connect(self.on_model_loaded)
        self.model_loader.error.connect(self.on_model_error)
        self.model_loader.start()

    def on_model_loaded(self, model):
        """Handle model loaded successfully"""
        self.model = model
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Model loaded successfully")
        self.transcribe_btn.setEnabled(True)

    def on_model_error(self, error):
        """Handle model loading error"""
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Model loading failed")
        QMessageBox.critical(self, "Error", f"Failed to load model:\n{error}")

    def on_model_changed(self, model_size):
        """Handle model selection change"""
        self.load_model(model_size)
        self.save_settings()

    def reload_current_model(self):
        """Reload current model"""
        self.model = None
        self.load_model(self.model_combo.currentText())

    def start_transcription(self):
        """Start audio transcription"""
        if not self.file_path_label.text() or self.file_path_label.text() == "No file selected":
            QMessageBox.warning(self, "Warning", "Please select an audio file first.")
            return

        if not self.model:
            QMessageBox.warning(self, "Warning", "Model not loaded. Please wait for model to load.")
            return

        # Prepare settings
        settings = {
            'auto_detect': self.auto_detect_cb.isChecked(),
            'translate': self.translate_cb.isChecked(),
            'timestamps': self.timestamps_cb.isChecked(),
            'language': None  # Auto-detect for now
        }

        # Start transcription
        self.transcription_worker = TranscriptionWorker(
            self.model,
            self.file_path_label.text(),
            settings
        )

        self.transcription_worker.progress.connect(self.update_status)
        self.transcription_worker.finished.connect(self.on_transcription_finished)
        self.transcription_worker.error.connect(self.on_transcription_error)

        self.transcription_worker.start()

        # Update UI
        self.transcribe_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

    def cancel_transcription(self):
        """Cancel ongoing transcription"""
        if self.transcription_worker:
            self.transcription_worker.cancel()
            self.transcription_worker.wait()

        self.transcribe_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Transcription cancelled")

    def on_transcription_finished(self, result):
        """Handle transcription completion"""
        self.transcribe_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

        # Update UI
        self.language_label.setText(f"Language: {result['language']}")
        self.transcription_text.setText(result['text'])

        # Enable save buttons
        self.save_txt_btn.setEnabled(True)
        self.copy_btn.setEnabled(True)

        # Add to history
        self.add_to_history(result)

        self.status_bar.showMessage("Transcription completed successfully")

    def on_transcription_error(self, error):
        """Handle transcription error"""
        self.transcribe_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Transcription failed")

        QMessageBox.critical(self, "Error", f"Transcription failed:\n{error}")

    def update_status(self, message):
        """Update status bar message"""
        self.status_bar.showMessage(message)

    def save_as_txt(self):
        """Save transcription as text file"""
        if not self.transcription_text.toPlainText():
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Transcription",
            "transcription.txt",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Language: {self.language_label.text()}\n\n")
                    f.write("Transcription:\n")
                    f.write(self.transcription_text.toPlainText())

                QMessageBox.information(self, "Success", f"Transcription saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")

    def copy_to_clipboard(self):
        """Copy transcription to clipboard"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.transcription_text.toPlainText())
        self.status_bar.showMessage("Copied to clipboard", 2000)

    def add_to_history(self, result):
        """Add transcription to history"""
        self.transcription_history.append(result)
        self.history_manager.add_transcription(result)

        # Add to history list
        item_text = f"{result['file_name']} - {result['language']} - {time.strftime('%Y-%m-%d %H:%M')}"
        item = QListWidgetItem(item_text)
        item.setData(Qt.UserRole, len(self.transcription_history) - 1)
        self.history_list.addItem(item)

    def show_history_item(self, item):
        """Show selected history item"""
        index = item.data(Qt.UserRole)
        result = self.transcription_history[index]

        info_text = f"""
        <b>File:</b> {result['file_name']}<br>
        <b>Language:</b> {result['language']}<br>
        <b>Path:</b> {result['file_path']}<br>
        """

        self.history_info.setText(info_text)
        self.history_text.setText(result['text'])
        self.export_history_btn.setEnabled(True)

    def export_history_item(self):
        """Export selected history item"""
        current_item = self.history_list.currentItem()
        if not current_item:
            return

        index = current_item.data(Qt.UserRole)
        result = self.transcription_history[index]

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Transcription",
            f"{os.path.splitext(result['file_name'])[0]}_transcription.txt",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            if self.history_manager.export_item(index, file_path):
                QMessageBox.information(self, "Success", f"Exported to:\n{file_path}")
            else:
                QMessageBox.critical(self, "Error", "Failed to export history item")

    def clear_history(self):
        """Clear transcription history"""
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear all transcription history?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.transcription_history.clear()
            self.history_list.clear()
            self.history_info.setText("Select an item to view details")
            self.history_text.clear()
            self.export_history_btn.setEnabled(False)
            self.history_manager.clear_history()

    def closeEvent(self, event):
        """Handle application close"""
        self.save_settings()

        # Cancel any running operations
        if self.transcription_worker and self.transcription_worker.isRunning():
            self.transcription_worker.cancel()
            self.transcription_worker.wait()

        if self.model_loader and self.model_loader.isRunning():
            self.model_loader.wait()

        event.accept()
