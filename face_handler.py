import cv2
import face_recognition
import numpy as np
import os
import pickle

# Configuration
DATASET_PATH = 'dataset'
MODEL_PATH = 'models/encodings.pickle'

def get_face_encodings():
    """Loads face encodings from a pickle file."""
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    return {"encodings": [], "names": [], "ids": []}

def save_face_encodings(data):
    """Saves face encodings to a pickle file."""
    os.makedirs('models', exist_ok=True)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(data, f)

def train_model():
    """Processes all images in the dataset and updates the encodings."""
    known_encodings = []
    known_names = []
    known_ids = []

    if not os.path.exists(DATASET_PATH):
        os.makedirs(DATASET_PATH)

    # dataset/Name_Roll/image.jpg
    for student_dir in os.listdir(DATASET_PATH):
        dir_path = os.path.join(DATASET_PATH, student_dir)
        if not os.path.isdir(dir_path):
            continue
        
        # Use rsplit to correctly handle names with underscores or spaces
        try:
            name, student_id = student_dir.rsplit('_', 1)
        except ValueError:
            print(f"DEBUG: Skipping invalid directory name: {student_dir}")
            continue

        print(f"DEBUG: Training images for {name} (ID: {student_id})...")
        for image_name in os.listdir(dir_path):
            image_path = os.path.join(dir_path, image_name)
            try:
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                
                if len(encodings) > 0:
                    known_encodings.append(encodings[0])
                    known_names.append(name)
                    known_ids.append(int(student_id))
            except Exception as e:
                print(f"DEBUG: Error processing {image_path}: {e}")
    
    data = {"encodings": known_encodings, "names": known_names, "ids": known_ids}
    save_face_encodings(data)
    return len(known_encodings)

def recognize_face(frame, known_data):
    """Detects and recognizes faces in a given frame."""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Detect face locations and encodings
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    face_names = []
    face_ids = []

    for face_encoding in face_encodings:
        # Compare with known faces (Lower tolerance = stricter)
        matches = face_recognition.compare_faces(known_data["encodings"], face_encoding, tolerance=0.5)
        name = "Unknown"
        student_id = None

        if True in matches:
            # Find the best match
            face_distances = face_recognition.face_distance(known_data["encodings"], face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_data["names"][best_match_index]
                student_id = known_data["ids"][best_match_index]
        
        face_names.append(name)
        face_ids.append(student_id)

    return face_locations, face_names, face_ids

def capture_sample(frame, student_name, student_roll, count):
    """Saves a frame as a dataset sample."""
    student_dir = f"{student_name}_{student_roll}"
    dir_path = os.path.join(DATASET_PATH, student_dir)
    os.makedirs(dir_path, exist_ok=True)
    
    image_path = os.path.join(dir_path, f"{count}.jpg")
    cv2.imwrite(image_path, frame)
    return True
