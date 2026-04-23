from flask import Flask, render_template, Response, request, redirect, url_for, flash, jsonify
import cv2
import os
import time
from database import init_db, add_student, mark_attendance, get_attendance_report, get_student_by_roll, get_all_students, delete_student
from face_handler import get_face_encodings, recognize_face, train_model, capture_sample

app = Flask(__name__)
app.secret_key = 'secret_key_for_session'

# Initialize Database
init_db()

# Global variables for camera handling
camera = None

def get_camera():
    global camera
    if camera is None or not camera.isOpened():
        # Try multiple indices if 0 fails (some laptops use 1 or 2)
        for index in [0, 1, 2]:
            print(f"DEBUG: Trying camera index {index}...")
            camera = cv2.VideoCapture(index)
            if camera.isOpened():
                print(f"DEBUG: Camera found at index {index}")
                return camera
        print("DEBUG: No camera found on any index!")
    return camera

def release_camera():
    global camera
    if camera is not None:
        camera.release()
        camera = None
        print("DEBUG: Camera released")

def gen_frames_register(student_name, student_id):
    """Video streaming generator for student registration."""
    cam = get_camera()
    if cam is None or not cam.isOpened():
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + b'' + b'\r\n')
        return

    count = 0
    max_samples = 10
    
    while count < max_samples:
        success, frame = cam.read()
        if not success:
            break
        else:
            # We'll use face_recognition for quality check
            import face_recognition
            face_locations = face_recognition.face_locations(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                
            if len(face_locations) > 0:
                # Capture sample using ID
                capture_sample(frame, student_name, student_id, count)
                count += 1
                cv2.putText(frame, f"Captured {count}/{max_samples}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.2) # Faster captures

def gen_frames_attendance():
    """Video streaming generator for real-time attendance."""
    cam = get_camera()
    if cam is None or not cam.isOpened():
        return
        
    known_data = get_face_encodings()
    
    while True:
        success, frame = cam.read()
        if not success:
            break
        else:
            # Recognize faces
            face_locations, face_names, face_ids = recognize_face(frame, known_data)
            
            for (top, right, bottom, left), name, student_id in zip(face_locations, face_names, face_ids):
                # Draw box
                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                
                # Automatically mark attendance
                if student_id:
                    success, msg = mark_attendance(student_id)
                    if success:
                        cv2.putText(frame, "Attendance Marked!", (left, bottom + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    else:
                        print(f"DEBUG: {msg}")

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    # Fetch top 5 recent attendance records
    records = get_attendance_report()[:5]
    return render_template('index.html', recent_records=records)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        roll = request.form.get('roll')
        if name and roll:
            # Check if student exists
            if get_student_by_roll(roll):
                flash("Student with this Roll Number already exists!", "danger")
                return redirect(url_for('register'))
            
            # Add to DB
            student_id = add_student(name, roll)
            return render_template('capture.html', name=name, roll=roll, student_id=student_id)
            
    return render_template('register.html')

@app.route('/video_feed_register/<name>/<roll>/<int:student_id>')
def video_feed_register(name, roll, student_id):
    return Response(gen_frames_register(name, student_id), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_attendance')
def video_feed_attendance():
    return Response(gen_frames_attendance(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/attendance')
def attendance():
    return render_template('attendance.html')

@app.route('/view_attendance')
def view_attendance():
    records = get_attendance_report()
    return render_template('view.html', records=records)

@app.route('/train')
def train():
    count = train_model()
    flash(f"Model trained successfully with {count} samples!", "success")
    return redirect(url_for('index'))

@app.route('/reset_camera')
def reset_camera():
    release_camera()
    flash("Camera system has been reset. Try opening it again.", "success")
    return redirect(url_for('index'))

import csv
from flask import send_file
import io

@app.route('/export_csv')
def export_csv():
    records = get_attendance_report()
    
    # Create a string buffer
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['ID', 'Name', 'Roll Number', 'Date', 'Time'])
    
    # Data
    for row in records:
        writer.writerow(row)
    
    output.seek(0)
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=attendance_report.csv"}
    )

@app.route('/students')
def students():
    all_students = get_all_students()
    return render_template('students.html', students=all_students)

@app.route('/delete_student/<int:student_id>')
def delete_student_route(student_id):
    delete_student(student_id)
    flash("Student and their records deleted successfully.", "success")
    return redirect(url_for('students'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
