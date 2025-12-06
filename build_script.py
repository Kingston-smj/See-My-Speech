#!/usr/bin/env python3
"""
Build script for creating Windows executable
Run this on Windows or use Wine/Docker
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_dependencies():
    """Install all required dependencies"""
    requirements = [
        "PyQt5>=5.15.0",
        "openai-whisper",
        "torch",
        "torchaudio",
        "psutil",
        "pydub",
        "pyinstaller"
    ]

    print("Installing dependencies...")
    for req in requirements:
        subprocess.check_call([sys.executable, "-m", "pip", "install", req])

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include any data files here
        # ('data_folder', 'data_folder'),
    ],
    hiddenimports=[
        'whisper',
        'torch',
        'torchaudio',
        'psutil',
        'pydub',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PIL._tkinter_finder',  # For audio processing
        'pkg_resources.py2_warn',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WhisperTranscription',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # Add your icon file
)
'''

    with open('whisper_app.spec', 'w') as f:
        f.write(spec_content)

def build_executable():
    """Build the executable using PyInstaller"""
    print("Creating PyInstaller spec file...")
    create_spec_file()

    print("Building executable...")
    subprocess.check_call([
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "whisper_app.spec"
    ])

def create_installer_script():
    """Create NSIS installer script"""
    nsis_script = '''
; NSIS Script for Whisper Transcription App
!include "MUI2.nsh"

Name "Whisper Audio Transcription"
OutFile "WhisperTranscription_Setup.exe"
InstallDir "$PROGRAMFILES\\WhisperTranscription"
InstallDirRegKey HKCU "Software\\WhisperTranscription" ""
RequestExecutionLevel admin

; Interface Settings
!define MUI_ABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    File /r "dist\\WhisperTranscription\\*"

    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\Whisper Transcription"
    CreateShortCut "$SMPROGRAMS\\Whisper Transcription\\Whisper Transcription.lnk" "$INSTDIR\\WhisperTranscription.exe"
    CreateShortCut "$DESKTOP\\Whisper Transcription.lnk" "$INSTDIR\\WhisperTranscription.exe"

    ; Registry entries
    WriteRegStr HKCU "Software\\WhisperTranscription" "" $INSTDIR
    WriteUninstaller "$INSTDIR\\Uninstall.exe"

    ; Add to Add/Remove Programs
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\WhisperTranscription" \\
                     "DisplayName" "Whisper Audio Transcription"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\WhisperTranscription" \\
                     "UninstallString" "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\*.*"
    RMDir /r "$INSTDIR"
    Delete "$SMPROGRAMS\\Whisper Transcription\\*.*"
    RMDir "$SMPROGRAMS\\Whisper Transcription"
    Delete "$DESKTOP\\Whisper Transcription.lnk"

    DeleteRegKey HKCU "Software\\WhisperTranscription"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\WhisperTranscription"
SectionEnd
'''

    with open('installer.nsi', 'w') as f:
        f.write(nsis_script)

def main():
    print("Building Windows executable for Whisper Transcription...")

    # Check if running on Windows
    if sys.platform != "win32":
        print("Warning: Building Windows executable on non-Windows platform")
        print("Consider using Wine or Docker for cross-compilation")

    try:
        install_dependencies()
        build_executable()
        create_installer_script()

        print("\nBuild completed successfully!")
        print("Executable created in: dist/WhisperTranscription/")
        print("To create installer, run: makensis installer.nsi")

    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()# This Python file uses the following encoding: utf-8

# if __name__ == "__main__":
#     pass
