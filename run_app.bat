@echo off
echo Starting Face Recognition Attendance System Setup...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python or Pip not found. Please ensure Python is installed and added to PATH.
    echo Also ensure CMake and VS Build Tools are installed for face_recognition.
    pause
    exit /b %errorlevel%
)
echo.
echo Starting Flask Server...
python app.py
pause
