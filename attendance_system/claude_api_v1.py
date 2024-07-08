from flask import Flask, request, jsonify, Response, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from marshmallow import Schema, fields
import base64
import io
import qrcode
from io import BytesIO
from datetime import datetime, timedelta, time
from PIL import Image, ImageDraw, ImageFont
import traceback
import cv2
import numpy as np
import logging
import os
# import time
from werkzeug.utils import secure_filename
from config import Config
from claude_face_recognition import FaceRecognition
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://laravel_user:laravel_user@localhost/attendance_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = Config.SECRET_KEY

db = SQLAlchemy(app)
migrate = Migrate(app, db)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Add these configurations to your Flask app
# app.config['TEMP_IMAGE_FOLDER'] = 'temp_images'
app.config['TEMP_IMAGE_FOLDER'] = os.path.abspath('temp_images')
app.config['MAX_TEMP_IMAGES'] = 5

# Ensure the temp folder exists
if not os.path.exists(app.config['TEMP_IMAGE_FOLDER']):
    os.makedirs(app.config['TEMP_IMAGE_FOLDER'])

def cleanup_temp_images():
    folder = app.config['TEMP_IMAGE_FOLDER']
    files = os.listdir(folder)
    if len(files) >= app.config['MAX_TEMP_IMAGES']:
        oldest_file = min(files, key=lambda f: os.path.getctime(os.path.join(folder, f)))
        os.remove(os.path.join(folder, oldest_file))

face_recognition = FaceRecognition.get_instance()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Models
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

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), db.ForeignKey('students.student_id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    end_time = db.Column(db.DateTime)
    class_id = db.Column(db.Integer, db.ForeignKey('Classes.class_id'), nullable=False)

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

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

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/api/register', methods=['POST'])
def register_student():
    try:
        logger.info("Received registration request")
        logger.info(f"Request form data: {request.form}")
        logger.info(f"Request files: {request.files}")

        if 'files' not in request.files:
            logger.error("No file part in the request")
            return jsonify({"error": "No file part"}), 400
        
        files = request.files.getlist('files')
        
        if not files or all(file.filename == '' for file in files):
            logger.error("No selected file")
            return jsonify({"error": "No selected file"}), 400

        logger.info(f"Number of files received: {len(files)}")

        name = request.form['name']
        student_id = request.form['student_id']
        email = request.form['email']
        password = request.form['password']
        academic_year = int(request.form['academic_year'])
        semester = request.form['semester']
        academic_type = request.form['academic_type']
        academic_group = request.form['academic_group']

        all_embeddings = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                logger.info(f"Saved file: {filepath}")
                
                image = cv2.imread(filepath)
                if image is None:
                    logger.error(f"Failed to read image: {filepath}")
                    os.remove(filepath)
                    continue

                faces = face_recognition.detect_faces(image)
                
                if len(faces) == 0:
                    logger.warning(f"No face detected in {filepath}")
                    os.remove(filepath)
                    continue
                
                if len(faces) > 1:
                    logger.warning(f"Multiple faces detected in {filepath}")
                    os.remove(filepath)
                    continue
                
                face = faces[0]
                aligned_face = face_recognition.align_face(image, face)
                
                if not face_recognition.is_valid_face(aligned_face):
                    logger.warning(f"Invalid face detected in {filepath}")
                    os.remove(filepath)
                    continue
                
                embeddings = face_recognition.get_multiple_embeddings(aligned_face)
                
                if embeddings:
                    all_embeddings.extend(embeddings)
                
                # Remove the file after processing
                os.remove(filepath)

        if not all_embeddings:
            return jsonify({"error": "No valid face found in the images. Please try again with clear, front-facing photos."}), 400

        # Hash the password before storing
        hashed_password = generate_password_hash(password)

        serializable_embeddings = [embedding.tolist() for embedding in all_embeddings]

        new_student = Student(
            student_id=student_id,
            name=name,
            email=email,
            password=hashed_password,
            academic_year=academic_year,
            semester=semester,
            academic_type=academic_type,
            academic_group=academic_group,
            face_embeddings=serializable_embeddings
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
            faces = face_recognition.detect_faces(image)
            
            os.remove(filepath)
            
            if not faces:
                return jsonify({"error": "No face found in the image"}), 400
            
            face = faces[0]
            aligned_face = face_recognition.align_face(image, face)
            input_embedding = face_recognition.get_face_embedding(aligned_face)
            
            if input_embedding is None:
                return jsonify({"error": "Failed to get face embedding"}), 400
            
            students = Student.query.all()
            
            for student in students:
                stored_embeddings = student.face_embeddings
                if face_recognition.recognize_face(input_embedding, stored_embeddings):
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

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    sessions = Session.query.all()
    return jsonify([{
        'id': session.id,
        'student_id': session.student_id,
        'start_time': session.start_time.isoformat(),
        'end_time': session.end_time.isoformat() if session.end_time else None,
        'class_id': session.class_id
    } for session in sessions]), 200

# @app.route('/api/students_list', methods=['GET'])
# def get_students():
#     students = Student.query.all()
#     return jsonify([{
#         'student_id': student.student_id,
#         'name': student.name
#     } for student in students]), 200

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
            Lecturer(first_name='Hawa', last_name='Nyende', email='hawa.nyende@example.com', password=generate_password_hash('password1')),
            Lecturer(first_name='Esther', last_name='Namirembe', email='esther.namirembe@example.com', password=generate_password_hash('password2')),
            Lecturer(first_name='Margaret', last_name='Nagwovuma', email='margaret.nagwovuma@example.com', password=generate_password_hash('password3')),
            Lecturer(first_name='Mercy', last_name='Amiyo', email='mercy.amiyo@example.com', password=generate_password_hash('password4')),
            Lecturer(first_name='Brian', last_name='Muchake', email='brian.muchake@example.com', password=generate_password_hash('password5'))
        ]
        db.session.bulk_save_objects(lecturers)
        db.session.commit()

        # Retrieve inserted lecturers
        inserted_lecturers = Lecturer.query.all()
        
        # Sample data for classes using retrieved lecturer IDs
        classes = [
            Class(class_name='IST 2102 Web Systems and Technologies I', lecturer_id=inserted_lecturers[0].lecturer_id),
            Class(class_name='IST 2104 Electronic Media Systems & Multimedia', lecturer_id=inserted_lecturers[1].lecturer_id),
            Class(class_name='BAM 2102 Entrepreneurship Principles', lecturer_id=inserted_lecturers[2].lecturer_id),
            Class(class_name='IST 2101 Data and Information Management II', lecturer_id=inserted_lecturers[3].lecturer_id),
            Class(class_name='IST 2103 Information System Security and Risk Management', lecturer_id=inserted_lecturers[4].lecturer_id)
        ]
        db.session.bulk_save_objects(classes)
        db.session.commit()

        # Retrieve inserted classes
        inserted_classes = Class.query.all()
        
        # Sample data for timetable
        timetable_entries = [
            Timetable(class_id=inserted_classes[0].class_id, day_of_week='Monday', start_time=time(8, 0), end_time=time(10, 0)),
            Timetable(class_id=inserted_classes[3].class_id, day_of_week='Monday', start_time=time(11, 0), end_time=time(13, 0)),
            Timetable(class_id=inserted_classes[4].class_id, day_of_week='Monday', start_time=time(14, 0), end_time=time(16, 0)),
            Timetable(class_id=inserted_classes[0].class_id, day_of_week='Tuesday', start_time=time(9, 0), end_time=time(11, 0)),
            Timetable(class_id=inserted_classes[3].class_id, day_of_week='Tuesday', start_time=time(11, 0), end_time=time(13, 0)),
            Timetable(class_id=inserted_classes[4].class_id, day_of_week='Tuesday', start_time=time(14, 0), end_time=time(16, 0)),
            Timetable(class_id=inserted_classes[1].class_id, day_of_week='Wednesday', start_time=time(8, 0), end_time=time(10, 0)),
            Timetable(class_id=inserted_classes[2].class_id, day_of_week='Wednesday', start_time=time(10, 0), end_time=time(11, 0)),
            Timetable(class_id=inserted_classes[3].class_id, day_of_week='Wednesday', start_time=time(11, 0), end_time=time(13, 0)),
            Timetable(class_id=inserted_classes[4].class_id, day_of_week='Wednesday', start_time=time(14, 0), end_time=time(16, 0)),
            Timetable(class_id=inserted_classes[1].class_id, day_of_week='Thursday', start_time=time(8, 0), end_time=time(10, 0)),
            Timetable(class_id=inserted_classes[2].class_id, day_of_week='Thursday', start_time=time(10, 0), end_time=time(11, 0)),
            Timetable(class_id=inserted_classes[3].class_id, day_of_week='Thursday', start_time=time(11, 0), end_time=time(13, 0)),
            Timetable(class_id=inserted_classes[4].class_id, day_of_week='Thursday', start_time=time(14, 0), end_time=time(16, 0)),
            Timetable(class_id=inserted_classes[1].class_id, day_of_week='Friday', start_time=time(8, 0), end_time=time(10, 0)),
            Timetable(class_id=inserted_classes[2].class_id, day_of_week='Friday', start_time=time(10, 0), end_time=time(11, 0)),
            Timetable(class_id=inserted_classes[3].class_id, day_of_week='Friday', start_time=time(11, 0), end_time=time(13, 0)),
            Timetable(class_id=inserted_classes[4].class_id, day_of_week='Friday', start_time=time(14, 0), end_time=time(16, 0))
        ]
        db.session.bulk_save_objects(timetable_entries)
        
        db.session.commit()
        return jsonify({"message": "Database populated with sample data!"}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error populating database: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('user_type')  # 'student' or 'lecturer'

        if user_type == 'student':
            user = Student.query.filter_by(email=email).first()
        elif user_type == 'lecturer':
            user = Lecturer.query.filter_by(email=email).first()
        else:
            return jsonify({"error": "Invalid user type"}), 400

        if user and check_password_hash(user.password, password):
            # In a real application, you would generate and return a JWT token here
            return jsonify({"message": "Login successful", "user_id": user.student_id if user_type == 'student' else user.lecturer_id}), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        logger.error(f"Error during login: {e}")
        return jsonify({"error": "Login failed"}), 500

@app.route('/api/class-attendance/<int:class_id>', methods=['GET'])
def get_class_attendance(class_id):
    try:
        # Get the class
        class_obj = Class.query.get(class_id)
        if not class_obj:
            return jsonify({"error": "Class not found"}), 404

        # Get the timetable entries for this class
        timetable_entries = Timetable.query.filter_by(class_id=class_id).all()

        # Get all attendance records for students in this class
        attendance_records = db.session.query(
            Attendance.id,
            Attendance.student_id,
            Student.name,
            Attendance.timestamp
        ).join(Student).filter(
            Student.academic_group == class_obj.class_name
        ).order_by(Attendance.timestamp.desc()).all()

        # Group attendance by date
        attendance_by_date = {}
        for record in attendance_records:
            date = record.timestamp.date()
            if date not in attendance_by_date:
                attendance_by_date[date] = []
            attendance_by_date[date].append({
                "id": record.id,
                "student_id": record.student_id,
                "name": record.name,
                "timestamp": record.timestamp.isoformat()
            })

        # Prepare the response
        response = {
            "class_name": class_obj.class_name,
            "timetable": [
                {
                    "day": entry.day_of_week,
                    "start_time": entry.start_time.isoformat(),
                    "end_time": entry.end_time.isoformat()
                }
                for entry in timetable_entries
            ],
            "attendance": [
                {
                    "date": date.isoformat(),
                    "records": records
                }
                for date, records in attendance_by_date.items()
            ]
        }

        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error fetching class attendance: {e}")
        return jsonify({"error": "Failed to fetch class attendance"}), 500

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

@app.route('/api/start-session', methods=['POST'])
def start_session():
    data = request.json
    student_id = data.get('student_id')
    class_id = data.get('class_id')

    # Check if there's an active session
    active_session = Session.query.filter_by(student_id=student_id, end_time=None).first()
    if active_session:
        return jsonify({"error": "There's already an active session for this student"}), 400

    # Create new session
    new_session = Session(student_id=student_id, class_id=class_id)
    db.session.add(new_session)
    db.session.commit()

    # Generate QR code
    # qr_data = f"http://yourdomain.com/end-session/{new_session.id}"
    qr_data = f"http://localhost:3000/end-session/{new_session.id}"
    qr_code = generate_qr_code(qr_data)

    return jsonify({
        "session_id": new_session.id,
        "qr_code": qr_code
    }), 201

@app.route('/api/end-session/<int:session_id>', methods=['POST'])
def end_session(session_id):
    try:
        data = request.json
        image_data = base64.b64decode(data['image'].split(',')[1])
        image = Image.open(io.BytesIO(image_data))
        
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        faces = face_recognition.detect_faces(opencv_image)
        
        if not faces:
            return jsonify({"success": False, "message": "No face detected"}), 400
        
        face = faces[0]
        aligned_face = face_recognition.align_face(opencv_image, face)
        input_embedding = face_recognition.get_face_embedding(aligned_face)
        
        if input_embedding is None:
            return jsonify({"success": False, "error": "Failed to get face embedding"}), 400
        
        session = Session.query.get(session_id)
        if not session:
            return jsonify({"success": False, "error": "Invalid session"}), 400

        student = Student.query.get(session.student_id)
        if not student:
            return jsonify({"success": False, "error": "Student not found"}), 400

        if face_recognition.recognize_face(input_embedding, student.face_embeddings):
            session.end_time = datetime.utcnow()
            db.session.commit()
            return jsonify({"success": True, "message": "Session ended successfully"}), 200
        else:
            return jsonify({"success": False, "message": "Face not recognized"}), 401

    except Exception as e:
        logger.error(f"Error ending session: {str(e)}")
        return jsonify({"success": False, "error": "Failed to end session"}), 500
        
@app.route('/api/live-recognition', methods=['POST'])
def live_recognition():
    try:
        data = request.json
        image_data = base64.b64decode(data['image'].split(',')[1])
        image = Image.open(io.BytesIO(image_data))
        
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        faces = face_recognition.detect_faces(opencv_image)
        
        if not faces:
            return jsonify({"matched": False, "message": "No face detected"}), 200
        
        face = faces[0]
        aligned_face = face_recognition.align_face(opencv_image, face)
        input_embedding = face_recognition.get_face_embedding(aligned_face)
        
        if input_embedding is None:
            return jsonify({"matched": False, "error": "Failed to get face embedding"}), 400
        
        students = Student.query.all()
        
        for student in students:
            stored_embeddings = student.face_embeddings
            if face_recognition.recognize_face(input_embedding, stored_embeddings):
                # Check for active session
                active_session = Session.query.filter_by(student_id=student.student_id, end_time=None).first()
                if not active_session:
                    # Start a new session
                    new_session = Session(student_id=student.student_id, class_id=1)  # Assuming class_id 1 for now
                    db.session.add(new_session)
                    db.session.commit()
                    
                    # Generate QR code
                    # qr_data = f"http://yourdomain.com/end-session/{new_session.id}"
                    qr_data = f"http://localhost:3000/end-session/{new_session.id}"
                    qr_code = generate_qr_code(qr_data)
                else:
                    qr_code = None

                # Draw bounding box and add text to the image
                draw = ImageDraw.Draw(image)
                draw.rectangle([face['box'][0], face['box'][1], face['box'][0] + face['box'][2], face['box'][1] + face['box'][3]], outline="green", width=2)
                
                font = ImageFont.load_default()
                text = f"{student.name} ({student.student_id})"
                draw.text((10, 10), text, font=font, fill="green")
                
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()

                image_filename = f"{student.student_id}_{int(datetime.utcnow().timestamp())}.jpg"
                image_path = os.path.join(app.config['TEMP_IMAGE_FOLDER'], image_filename)
                image.save(image_path)
                
                cleanup_temp_images()

                return jsonify({
                    "matched": True,
                    "student_id": student.student_id,
                    "name": student.name,
                    "image_filename": image_filename,
                    "qr_code": qr_code
                }), 200

        return jsonify({"matched": False, "message": "Face detected but not recognized"}), 200
    except Exception as e:
        logger.error(f"Error in live recognition: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"matched": False, "error": "Failed to process image"}), 500

@app.route('/temp_image/<filename>')
def serve_temp_image(filename):
    app.logger.debug(f'Requested filename: {filename}')
    file_path = os.path.join(app.config['TEMP_IMAGE_FOLDER'], filename)
    app.logger.debug(f'Full file path: {file_path}')
    if os.path.exists(file_path):
        app.logger.debug(f'File exists: {file_path}')
        try:
            return send_from_directory(app.config['TEMP_IMAGE_FOLDER'], filename, as_attachment=True)
        except Exception as e:
            app.logger.error(f'Error serving file: {e}')
            return 'Error serving file', 500
    else:
        app.logger.error(f'File not found: {file_path}')
        return 'File not found', 404

@app.route('/api/student/<string:student_id>/attendance', methods=['GET'])
def get_student_attendance(student_id):
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404

        attendance_records = Attendance.query.filter_by(student_id=student_id).order_by(Attendance.timestamp.desc()).all()

        attendance_list = [
            {
                "id": record.id,
                "timestamp": record.timestamp.isoformat()
            }
            for record in attendance_records
        ]

        response = {
            "student_id": student.student_id,
            "name": student.name,
            "academic_group": student.academic_group,
            "attendance": attendance_list
        }

        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error fetching student attendance: {e}")
        return jsonify({"error": "Failed to fetch student attendance"}), 500

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        db.create_all()
    app.run(debug=True, use_reloader=False)