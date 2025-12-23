"""
Build script to create .exe file from the media player application
Run: python build_exe.py
"""
import PyInstaller.__main__
import sys

print("Building executable...")
print("This may take a few minutes...")

# PyInstaller options
options = [
    'main.py',
    '--name=MediaPlayer',
    '--onefile',
    '--windowed',
    '--hidden-import=PyQt6',
    '--collect-all=PyQt6',
    '--noconsole',
    '--clean',
]

PyInstaller.__main__.run(options)

print("\n" + "="*50)
print("Build complete! The .exe file should be in the 'dist' folder.")
print("="*50)
print("\nThe application uses only Python libraries - no external dependencies needed!")

