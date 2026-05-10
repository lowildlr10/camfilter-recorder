@echo off
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo Building with PyInstaller (--onedir for fast startup)...
pyinstaller ^
  --onedir ^
  --windowed ^
  --name "CamFilterRecorder" ^
  main.py

echo.
echo Done! The app folder is at dist\CamFilterRecorder\
echo Run dist\CamFilterRecorder\CamFilterRecorder.exe to test it.
pause
