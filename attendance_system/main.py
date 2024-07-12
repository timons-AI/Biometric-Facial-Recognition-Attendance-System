import cv2
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from claude_face_recognition import FaceRecognition
from api_v2 import Student, User
import time
import os

# Database connection
DATABASE_URI = 'mysql+pymysql://laravel_user:laravel_user@localhost/attendance_system_v1'
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

# Initialize FaceRecognition
face_recognition = FaceRecognition.get_instance()

def load_students():
    session = Session()
    students = session.query(Student).all()
    student_data = []
    for student in students:
        if student.face_encoding:
            student_data.append({
                'id': student.id,
                'name': student.name,
                'face_encoding': [np.array(encoding) for encoding in student.face_encoding]
            })
    session.close()
    return student_data

def recognize_face(face_embedding, students):
    best_match = None
    best_distance = float('inf')
    for student in students:
        is_match, distance = face_recognition.recognize_face(face_embedding, student['face_encoding'])
        if is_match and distance < best_distance:
            best_match = student
            best_distance = distance
    return best_match

def main():
    students = load_students()
    print(f"Loaded {len(students)} students")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Create a directory to save the processed frames (in case display fails)
    output_dir = "processed_frames"
    os.makedirs(output_dir, exist_ok=True)

    frame_count = 0
    display_enabled = True

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        # Detect faces
        faces = face_recognition.detect_faces(frame)

        for face in faces:
            (x, y, w, h) = face['box']
            face_img = frame[y:y+h, x:x+w]
            
            # Align and get embedding
            aligned_face = face_recognition.align_face(frame, face)
            face_embedding = face_recognition.get_face_embedding(aligned_face)

            if face_embedding is not None:
                # Recognize face
                matched_student = recognize_face(face_embedding, students)

                # Draw bounding box
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                # Display name
                if matched_student:
                    name = matched_student['name']
                    cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        if display_enabled:
            try:
                cv2.imshow('Face Recognition', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            except cv2.error:
                print("Warning: Unable to display video. Falling back to saving frames.")
                display_enabled = False

        if not display_enabled:
            # Save the processed frame
            output_path = os.path.join(output_dir, f"frame_{frame_count:04d}.jpg")
            cv2.imwrite(output_path, frame)
            print(f"Saved processed frame: {output_path}")

        frame_count += 1
        time.sleep(0.1)  # Add a small delay to reduce CPU usage

    cap.release()
    cv2.destroyAllWindows()
    print("Processing complete.")
    if not display_enabled:
        print("Check the 'processed_frames' directory for saved frames.")

if __name__ == "__main__":
    main()