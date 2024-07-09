from flask import Flask, request, jsonify
from flask_cors import CORS
from database import Database
from face_recognition import FaceRecognition
import cv2
import numpy as np
import logging
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)
db = Database()
face_recognition = FaceRecognition.get_instance()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/register', methods=['POST'])
def register_student():
    try:
        name = request.form['name']
        student_id = request.form['student_id']
        
        if 'files' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        files = request.files.getlist('files')
        
        if not files:
            return jsonify({"error": "No selected file"}), 400
        
        embeddings = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                image = cv2.imread(filepath)
                faces = face_recognition.detect_faces(image)
                
                if len(faces) != 1:
                    os.remove(filepath)
                    return jsonify({"error": "Image must contain exactly one face"}), 400
                
                (x, y, w, h) = faces[0]
                face_image = image[y:y+h, x:x+w]
                
                if not face_recognition.is_valid_face(face_image):
                    os.remove(filepath)
                    return jsonify({"error": "Invalid face detected"}), 400
                
                face_embedding = face_recognition.get_face_embedding(face_image)
                
                if face_embedding is not None:
                    embeddings.append(face_embedding)
                
                os.remove(filepath)
        
        if not embeddings:
            return jsonify({"error": "No valid face found in the images"}), 400
        
        # Average the embeddings
        average_embedding = np.mean(embeddings, axis=0)
        
        query = "INSERT INTO students (student_id, name, face_embedding) VALUES (%s, %s, %s)"
        params = (student_id, name, average_embedding.tobytes())
        db.execute_query(query, params)

        return jsonify({"message": "Student registered successfully"}), 201
    except Exception as e:
        logger.error(f"Error registering student: {e}")
        return jsonify({"error": "Failed to register student"}), 500
        
@app.route('/api/recognize', methods=['POST'])
def recognize_student():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            image = cv2.imread(filepath)
            face_embedding = face_recognition.get_face_embedding(image)
            
            os.remove(filepath)  # Remove the file after processing
            
            if face_embedding is None:
                return jsonify({"error": "No face found in the image"}), 400
            
            # Fetch all students from the database
            query = "SELECT student_id, name, face_embedding FROM students"
            results = db.fetch_all(query)
            
            if results is None:
                return jsonify({"error": "Failed to fetch students from database"}), 500
            
            for student_id, name, stored_embedding_bytes in results:
                stored_embedding = np.frombuffer(stored_embedding_bytes, dtype=np.float32)
                if face_recognition.compare_faces(face_embedding, stored_embedding):
                    # Record attendance
                    attendance_query = "INSERT INTO attendance (student_id, timestamp) VALUES (%s, NOW())"
                    db.execute_query(attendance_query, (student_id,))
                    return jsonify({"student_id": student_id, "name": name}), 200
            
            return jsonify({"message": "No matching student found"}), 404
    except Exception as e:
        logger.error(f"Error recognizing student: {e}")
        return jsonify({"error": "Failed to recognize student"}), 500


@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    try:
        query = """
        SELECT a.id, a.student_id, s.name, a.timestamp 
        FROM attendance a 
        JOIN students s ON a.student_id = s.student_id 
        ORDER BY a.timestamp DESC
        """
        results = db.fetch_all(query)
        
        if results is None:
            return jsonify({"error": "Failed to fetch attendance records"}), 500
        
        attendance_records = [
            {
                "id": record[0],
                "student_id": record[1],
                "name": record[2],
                "timestamp": record[3].isoformat()
            }
            for record in results
        ]
        
        return jsonify(attendance_records), 200
    except Exception as e:
        logger.error(f"Error fetching attendance: {e}")
        return jsonify({"error": "Failed to fetch attendance records"}), 500


@app.route('/api/students', methods=['GET'])
def get_students():
    try:
        query = "SELECT student_id, name FROM students"
        results = db.fetch_all(query)
        
        if results is None:
            return jsonify({"error": "Failed to fetch students"}), 500
        
        students = [
            {
                "student_id": record[0],
                "name": record[1]
            }
            for record in results
        ]
        
        return jsonify(students), 200
    except Exception as e:
        logger.error(f"Error fetching students: {e}")
        return jsonify({"error": "Failed to fetch students"}), 500


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, use_reloader=False)  