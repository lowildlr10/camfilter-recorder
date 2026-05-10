"""
Quick-start script — installs dependencies into a virtual environment
and launches the app. Works on Windows, macOS, and Linux.

Usage:  python install_and_run.py
"""
import subprocess
import sys
import os
import venv
from pathlib import Path

VENV_DIR = Path(__file__).parent / ".venv"
REQUIREMENTS = Path(__file__).parent / "requirements.txt"
MAIN = Path(__file__).parent / "main.py"

def pip(*args):
    python = VENV_DIR / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    subprocess.check_call([str(python), "-m", "pip", *args])

def main():
    if not VENV_DIR.exists():
        print("Creating virtual environment…")
        venv.create(str(VENV_DIR), with_pip=True)

    print("Installing / checking dependencies…")
    pip("install", "--quiet", "--upgrade", "pip")
    pip("install", "--quiet", "-r", str(REQUIREMENTS))

    python = VENV_DIR / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    print("Launching CamFilter Recorder…")
    os.execv(str(python), [str(python), str(MAIN)])

if __name__ == "__main__":
    main()
