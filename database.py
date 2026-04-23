import sqlite3
from datetime import datetime
import os
import threading

DB_PATH = 'attendance.db'
db_lock = threading.Lock()

def init_db():
    """Initializes the SQLite database and creates necessary tables."""
    with db_lock:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
    
    # Table for students
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_number TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Table for attendance
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_student(name, roll_number):
    """Adds a new student to the database."""
    with db_lock:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO students (name, roll_number) VALUES (?, ?)', (name, roll_number))
            conn.commit()
            student_id = cursor.lastrowid
            conn.close()
            return student_id
        except sqlite3.IntegrityError:
            return None

def get_student_by_roll(roll_number):
    """Fetches a student ID by roll number."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM students WHERE roll_number = ?', (roll_number,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def mark_attendance(student_id):
    """Marks attendance for a student if not already marked today."""
    today = datetime.now().strftime('%Y-%m-%d')
    now_time = datetime.now().strftime('%H:%M:%S')
    
    with db_lock:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if attendance is already marked for today
        cursor.execute('SELECT * FROM attendance WHERE student_id = ? AND date = ?', (student_id, today))
        if cursor.fetchone():
            conn.close()
            return False, "Attendance already marked for today."
    
    # Mark attendance
    try:
        cursor.execute('INSERT INTO attendance (student_id, date, time) VALUES (?, ?, ?)', (student_id, today, now_time))
        conn.commit()
        print(f"DEBUG: Successfully marked attendance for student_id {student_id}")
        conn.close()
        return True, "Attendance marked successfully."
    except Exception as e:
        print(f"DEBUG: Database error: {e}")
        conn.close()
        return False, str(e)

def get_all_students():
    """Fetches all registered students."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    conn.close()
    return students

def delete_student(student_id):
    """Deletes a student and their attendance records."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM attendance WHERE student_id = ?', (student_id,))
    cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()
    return True

def get_attendance_report():
    """Fetches complete attendance report with student names."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.id, s.name, s.roll_number, a.date, a.time
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        ORDER BY a.date DESC, a.time DESC
    ''')
    records = cursor.fetchall()
    conn.close()
    return records

if __name__ == '__main__':
    init_db()
    print("Database initialized.")
