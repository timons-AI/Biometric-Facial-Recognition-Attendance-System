from flask import Blueprint, request, jsonify, current_app
from app.services.face_recognition_service import train_model, recognize_face
from app.models.student import Student, FaceImage
from app.models.attendance import Attendance
from app import db
import os
import logging
from flask_cors import CORS

logging.basicConfig(level=logging.INFO)

bp = Blueprint('api', __name__)
CORS(bp)

def cleanup_old_images(filenames):
    for filename in filenames:
        try:
            if os.path.isfile(filename):
                os.unlink(filename)
        except Exception as e:
            logging.error(f'Failed to delete {filename}. Reason: {e}')

@bp.route('/register', methods=['POST'])
def register_student():
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    if 'files' not in request.files:
        return jsonify({"error": "No file part"}), 400
    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No selected file"}), 400
    
    student_name = request.form.get('name')
    student_id = request.form.get('student_id')

    if not student_name or not student_id:
        return jsonify({"error": "Missing student name or ID"}), 400

    existing_student = Student.query.filter_by(student_id=student_id).first()
    if existing_student:
        return jsonify({"error": "Student with this ID already exists"}), 400
    
    new_student = Student(name=student_name, student_id=student_id)

    face_images = []
    temp_filenames = []
    for file in files:
        if file:
            filename = os.path.join(upload_folder, f"{student_id}_{file.filename}")
            file.save(filename)
            temp_filenames.append(filename)
            face_images.append(filename)

    try:
        all_students = Student.query.all()
        
        all_image_paths = []
        all_labels = []
        for student in all_students:
            student_images = [image.filename for image in student.face_images]
            all_image_paths.extend(student_images)
            all_labels.extend([student.student_id] * len(student_images))
        
        all_image_paths.extend(face_images)
        all_labels.extend([student_id] * len(face_images))
        
        if len(all_labels) > 0:
            train_model(all_image_paths, all_labels)
            
            db.session.add(new_student)
            for filename in temp_filenames:
                new_image = FaceImage(filename=filename, student=new_student)
                db.session.add(new_image)
            
            db.session.commit()
            logging.info(f"Student registered successfully. ID: {student_id}, Name: {student_name}")            
            return jsonify({"message": "Student registered successfully"}), 201
        else:
            cleanup_old_images(temp_filenames)
            return jsonify({"error": "No valid images for training"}), 400

    except Exception as e:
        cleanup_old_images(temp_filenames)
        logging.error(f"Error during model training: {e}")
        return jsonify({"error": f"Failed to train model: {str(e)}"}), 500

@bp.route('/recognize', methods=['POST'])
def recognize():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        filename = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        predicted_id, confidence = recognize_face(filename)
        
        if predicted_id is None:
            return jsonify({"error": "Face recognition failed"}), 500
        
        logging.info(f"Predicted ID: {predicted_id}, Confidence: {confidence}")
        
        student = Student.query.filter_by(student_id=predicted_id).first()
        
        if student:
            attendance = Attendance(student_id=student.id)
            db.session.add(attendance)
            db.session.commit()
            return jsonify({"message": "Attendance logged successfully", "student": student.name, "confidence": float(confidence)}), 200
        else:
            return jsonify({"error": "Student not found in database", "predicted_id": predicted_id}), 404

    return jsonify({"error": "File processing failed"}), 500

@bp.route('/attendance', methods=['GET'])
def get_attendance():
    attendance_records = Attendance.query.all()
    return jsonify([
        {"student_id": record.student_id, "check_in": record.check_in.isoformat()}
        for record in attendance_records
    ]), 200

@bp.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([
        {"id": student.id, "name": student.name, "student_id": student.student_id}
        for student in students
    ]), 200

@bp.route('/format', methods=['GET'])
def format():
    db.drop_all()
    db.create_all()
    
    if os.path.exists('models/face_classifier.pkl'):
        os.remove('models/face_classifier.pkl')
    
    cleanup_old_images(current_app.config['UPLOAD_FOLDER'])
    
    return jsonify({"message": "Database, models, and uploads cleared successfully"}), 200