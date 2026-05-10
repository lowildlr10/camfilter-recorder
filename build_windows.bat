@echo off
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo Building executable...
pyinstaller ^
  --onefile ^
  --windowed ^
  --name "CamFilterRecorder" ^
  --add-data "filters.py;." ^
  main.py

echo Done! Find CamFilterRecorder.exe in the dist\ folder.
pause
