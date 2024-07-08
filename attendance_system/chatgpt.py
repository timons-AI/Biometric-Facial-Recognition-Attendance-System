import cv2
import numpy as np
from mtcnn import MTCNN
from werkzeug.security import generate_password_hash
from marshmallow import Schema, fields
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
import logging
import datetime
from werkzeug.utils import secure_filename
from face_recognition import FaceRecognition


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://laravel_user:laravel_user@localhost/attendance_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s', handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

detector = MTCNN()

class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    academic_year = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.String(10), nullable=False)
    academic_type = db.Column(db.String(20), nullable=False)
    academic_group = db.Column(db.String(20), nullable=False)
    face_embeddings = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), db.ForeignKey('students.student_id'), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class Lecturer(db.Model):
    __tablename__ = 'Lecturers'
    lecturer_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Class(db.Model):
    __tablename__ = 'Classes'
    class_id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(100), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('Lecturers.lecturer_id'))

class Timetable(db.Model):
    __tablename__ = 'Timetable'
    timetable_id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('Classes.class_id'))
    day_of_week = db.Column(db.Enum('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

# Schemas
class LecturerSchema(Schema):
    lecturer_id = fields.Int(dump_only=True)
    first_name = fields.Str()
    last_name = fields.Str()

class ClassSchema(Schema):
    class_id = fields.Int(dump_only=True)
    class_name = fields.Str()
    lecturer_id = fields.Int()

class TimetableSchema(Schema):
    timetable_id = fields.Int(dump_only=True)
    class_id = fields.Int()
    day_of_week = fields.Str()
    start_time = fields.Time()
    end_time = fields.Time()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

@app.route('/api/register', methods=['POST'])
def register_student():
    try:
        if 'files' not in request.files:
            return jsonify({"error": "No file part"}), 400
        files = request.files.getlist('files')
        if not files or all(file.filename == '' for file in files):
            return jsonify({"error": "No selected file"}), 400

        name = request.form['name']
        student_id = request.form['student_id']
        email = request.form['email']
        password = request.form['password']
        academic_year = int(request.form['academic_year'])
        semester = request.form['semester']
        academic_type = request.form['academic_type']
        academic_group = request.form['academic_group']

        embeddings = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                image = cv2.imread(filepath)
                faces = detector.detect_faces(image)
                
                if len(faces) != 1:
                    logger.warning(f"Invalid face count in {filepath}")
                    os.remove(filepath)
                    continue
                
                (x, y, w, h) = faces[0]['box']
                face_image = image[y:y+h, x:x+w]
                face_embedding = face_recognition.get_face_embedding(face_image)
                
                if face_embedding is not None:
                    embeddings.append(face_embedding.tolist())
                
                os.remove(filepath)

        if not embeddings:
            return jsonify({"error": "No valid face found in the images. Please try again with clear, front-facing photos."}), 400

        hashed_password = generate_password_hash(password)
        
        new_student = Student(
            student_id=student_id,
            name=name,
            email=email,
            password=hashed_password,
            academic_year=academic_year,
            semester=semester,
            academic_type=academic_type,
            academic_group=academic_group,
            face_embeddings=embeddings
        )
        db.session.add(new_student)
        db.session.commit()

        return jsonify({"message": "Student registered successfully"}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error registering student: {e}")
        return jsonify({"error": str(e)}), 500

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
            
            os.remove(filepath)
            
            if face_embedding is None:
                return jsonify({"error": "No face found in the image"}), 400
            
            students = Student.query.all()
            
            for student in students:
                embeddings = student.face_embeddings
                for stored_embedding in embeddings:
                    stored_embedding = np.array(stored_embedding)
                    if face_recognition.compare_faces(face_embedding, stored_embedding):
                        new_attendance = Attendance(student_id=student.student_id)
                        db.session.add(new_attendance)
                        db.session.commit()
                        return jsonify({"student_id": student.student_id, "name": student.name}), 200
            
            return jsonify({"message": "No matching student found"}), 404
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error recognizing student: {e}")
        return jsonify({"error": "Failed to recognize student"}), 500

@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    try:
        attendance_records = db.session.query(
            Attendance.id,
            Attendance.student_id,
            Student.name,
            Attendance.timestamp
        ).join(Student).order_by(Attendance.timestamp.desc()).all()
        
        attendance_list = [
            {
                "id": record.id,
                "student_id": record.student_id,
                "name": record.name,
                "timestamp": record.timestamp.isoformat()
            }
            for record in attendance_records
        ]
        
        return jsonify(attendance_list), 200
    except Exception as e:
        logger.error(f"Error fetching attendance: {e}")
        return jsonify({"error": "Failed to fetch attendance records"}), 500

@app.route('/api/students', methods=['GET'])
def get_students():
    try:
        students = Student.query.all()
        
        student_list = [
            {
                "student_id": student.student_id,
                "name": student.name,
                "email": student.email,
                "academic_year": student.academic_year,
                "semester": student.semester,
                "academic_type": student.academic_type,
                "academic_group": student.academic_group
            }
            for student in students
        ]
        
        return jsonify(student_list), 200
    except Exception as e:
        logger.error(f"Error fetching students: {e}")
        return jsonify({"error": "Failed to fetch students"}), 500

@app.route('/api/lecturers', methods=['GET'])
def get_lecturers():
    lecturers = Lecturer.query.all()
    return jsonify(LecturerSchema(many=True).dump(lecturers)), 200

@app.route('/api/classes', methods=['GET'])
def get_classes():
    classes = Class.query.all()
    return jsonify(ClassSchema(many=True).dump(classes)), 200

@app.route('/api/timetable', methods=['GET'])
def get_timetable():
    timetable = Timetable.query.all()
    return jsonify(TimetableSchema(many=True).dump(timetable)), 200

@app.route('/populate', methods=['GET'])
def populate_database():
    try:
        # Sample data for lecturers
        lecturers = [
            Lecturer(first_name='Hawa', last_name='Nyende', email='hawa.nyende@example.com', password='hashed_password1'),
            Lecturer(first_name='Esther', last_name='Namirembe', email='esther.namirembe@example.com', password='hashed_password2'),
            Lecturer(first_name='Margaret', last_name='Nagwovuma', email='margaret.nagwovuma@example.com', password='hashed_password3'),
            Lecturer(first_name='Mercy', last_name='Amiyo', email='mercy.amiyo@example.com', password='hashed_password4'),
            Lecturer(first_name='Brian', last_name='Muchake', email='brian.muchake@example.com', password='hashed_password5')
        ]
        db.session.bulk_save_objects(lecturers)
        
        # Sample data for classes
        classes = [
            Class(class_name='IST 2102 Web Systems and Technologies I', lecturer_id=1),
            Class(class_name='IST 2104 Electronic Media Systems & Multimedia', lecturer_id=2),
            Class(class_name='BAM 2102 Entrepreneurship Principles', lecturer_id=3),
            Class(class_name='IST 2101 Data and Information Management II', lecturer_id=4),
            Class(class_name='IST 2103 Information System Security and Risk Management', lecturer_id=5)
        ]
        db.session.bulk_save_objects(classes)
        
        # Sample data for timetable
        timetable_entries = [
            Timetable(class_id=1, day_of_week='Monday', start_time=datetime.time(8, 0), end_time=datetime.time(10, 0)),
            Timetable(class_id=4, day_of_week='Monday', start_time=datetime.time(11, 0), end_time=datetime.time(13, 0)),
            Timetable(class_id=5, day_of_week='Monday', start_time=datetime.time(14, 0), end_time=datetime.time(16, 0)),
            Timetable(class_id=1, day_of_week='Tuesday', start_time=datetime.time(9, 0), end_time=datetime.time(11, 0)),
            Timetable(class_id=4, day_of_week='Tuesday', start_time=datetime.time(11, 0), end_time=datetime.time(13, 0)),
            Timetable(class_id=5, day_of_week='Tuesday', start_time=datetime.time(14, 0), end_time=datetime.time(16, 0)),
            Timetable(class_id=2, day_of_week='Wednesday', start_time=datetime.time(8, 0), end_time=datetime.time(10, 0)),
            Timetable(class_id=3, day_of_week='Wednesday', start_time=datetime.time(10, 0), end_time=datetime.time(11, 0)),
            Timetable(class_id=4, day_of_week='Wednesday', start_time=datetime.time(11, 0), end_time=datetime.time(13, 0)),
            Timetable(class_id=5, day_of_week='Wednesday', start_time=datetime.time(14, 0), end_time=datetime.time(16, 0)),
            Timetable(class_id=2, day_of_week='Thursday', start_time=datetime.time(8, 0), end_time=datetime.time(10, 0)),
            Timetable(class_id=3, day_of_week='Thursday', start_time=datetime.time(10, 0), end_time=datetime.time(11, 0)),
            Timetable(class_id=4, day_of_week='Thursday', start_time=datetime.time(11, 0), end_time=datetime.time(13, 0)),
            Timetable(class_id=5, day_of_week='Thursday', start_time=datetime.time(14, 0), end_time=datetime.time(16, 0)),
            Timetable(class_id=2, day_of_week='Friday', start_time=datetime.time(8, 0), end_time=datetime.time(10, 0)),
            Timetable(class_id=3, day_of_week='Friday', start_time=datetime.time(10, 0), end_time=datetime.time(11, 0)),
            Timetable(class_id=4, day_of_week='Friday', start_time=datetime.time(11, 0), end_time=datetime.time(13, 0)),
            Timetable(class_id=5, day_of_week='Friday', start_time=datetime.time(14, 0), end_time=datetime.time(16, 0))
        ]
        db.session.bulk_save_objects(timetable_entries)
        
        db.session.commit()
        return jsonify({"message": "Database populated with sample data!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        db.create_all()
    app.run(debug=True, use_reloader=False)
