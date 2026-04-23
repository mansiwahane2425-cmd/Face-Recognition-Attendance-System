# Face Recognition Attendance System

A premium, offline face recognition attendance system built with Python, Flask, OpenCV, and SQLite.

## Features
- **Student Registration**: Capture multiple face samples via webcam.
- **Real-time Recognition**: Automatically mark attendance when a face is detected.
- **Offline First**: No external APIs or internet required.
- **Premium UI**: Modern "Glassmorphism" design with dark mode.
- **Security**: Local SQLite database and local image storage.

## Prerequisites
- Python 3.8 or higher.
- [CMake](https://cmake.org/download/) (Required for `dlib`).
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (C++ Compiler for Windows).

## Setup Instructions

### 1. Install Dependencies
Open your terminal in the project folder and run:
```bash
pip install -r requirements.txt
```
*Note: If `dlib` fails to install, ensure you have CMake and Visual Studio C++ build tools installed.*

### 2. Run the Application
```bash
python app.py
```

### 3. Usage Guide
1. **Dashboard**: Navigate to `http://localhost:5000`.
2. **Register**: Go to the "Register" page, enter student details, and capture face samples.
3. **Train**: Click the "Train Model" button in the navigation bar to process the new samples.
4. **Attendance**: Open the "Attendance" page to start real-time recognition.
5. **View Records**: Check the "Records" page for the history of attendance.

## Project Structure
- `app.py`: Flask application and video streaming.
- `database.py`: SQLite database logic.
- `face_handler.py`: Face encoding and recognition logic.
- `dataset/`: Stores captured student images.
- `models/`: Stores serialized face encodings.
- `templates/`: HTML interface files.
- `static/`: CSS and assets.

## Troubleshooting
- **Camera not opening**: Ensure no other application (like Zoom or Teams) is using the webcam.
- **No faces detected**: Ensure there is proper lighting and you are facing the camera directly.
- **Dlib Installation Error**: On Windows, `dlib` usually requires `msvc` compiler. Install "Desktop development with C++" workload from Visual Studio Installer.
