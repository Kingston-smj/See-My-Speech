"""
Theme definitions for the application
"""

LIGHT_THEME = """
QMainWindow { background-color: #f5f5f5; }
QGroupBox { border: 2px solid #cccccc; border-radius: 5px; margin-top: 1ex; padding-top: 10px; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }
QPushButton { background-color: #4CAF50; border: none; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
QPushButton:hover { background-color: #45a049; }
QPushButton:pressed { background-color: #3d8b40; }
QPushButton:disabled { background-color: #cccccc; color: #666666; }
QTextEdit { border: 1px solid #cccccc; border-radius: 4px; padding: 5px; font-family: 'Consolas', 'Monaco', monospace; }
QTabWidget::pane { border: 1px solid #cccccc; }
QTabBar::tab { background-color: #e1e1e1; padding: 8px 16px; margin-right: 2px; }
QTabBar::tab:selected { background-color: #4CAF50; color: white; }
"""

DARK_THEME = """
QMainWindow { background-color: #121212; color: #e0e0e0; }
QWidget { background-color: #121212; color: #e0e0e0; }
QGroupBox { border: 2px solid #cccccc; border-radius: 5px; margin-top: 1ex; padding-top: 10px; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }
QPushButton { background-color: #1e1e1e; border: 1px solid #444; color: #e0e0e0; padding: 6px 12px; border-radius: 4px; }
QPushButton:hover { background-color: #2a2a2a; }
QTextEdit { background-color: #1a1a1a; color: #e0e0e0; border: 1px solid #333; }
QTabBar::tab { background: #1e1e1e; color: #e0e0e0; padding: 8px 16px; }
QTabBar::tab:selected { background: #17631a; color:black; }
"""

#QGroupBox { border: 1px solid #333; }