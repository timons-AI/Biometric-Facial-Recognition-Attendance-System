from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import base64
import io
import qrcode
from io import BytesIO
import cv2
import numpy as np
import logging
import os
from werkzeug.utils import secure_filename
import face_recognition
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://laravel_user:laravel_user@localhost/attendance_system_v1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TEMP_IMAGE_FOLDER'] = os.path.abspath('temp_images')
app.config['MAX_TEMP_IMAGES'] = 5

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Ensure the temp folder exists
if not os.path.exists(app.config['TEMP_IMAGE_FOLDER']):
    os.makedirs(app.config['TEMP_IMAGE_FOLDER'])

# Models
class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    face_encodings = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Lecturer(db.Model):
    __tablename__ = 'lecturers'
    lecturer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Admin(db.Model):
    __tablename__ = 'admins'
    admin_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Course(db.Model):
    __tablename__ = 'courses'
    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturers.lecturer_id'))

class Timetable(db.Model):
    __tablename__ = 'timetable'
    timetable_id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'))
    day_of_week = db.Column(db.Enum('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

class Session(db.Model):
    __tablename__ = 'sessions'
    session_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), db.ForeignKey('students.student_id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.Enum('active', 'ended'), nullable=False, default='active')

# Schemas
class StudentSchema(Schema):
    student_id = fields.Str(required=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)

class LecturerSchema(Schema):
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

class CourseSchema(Schema):
    course_name = fields.Str(required=True)
    lecturer_id = fields.Int(required=True)

class TimetableSchema(Schema):
    course_id = fields.Int(required=True)
    day_of_week = fields.Str(required=True, validate=validate.OneOf(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']))
    start_time = fields.Time(required=True)
    end_time = fields.Time(required=True)

# Initialize schemas
student_schema = StudentSchema()
lecturer_schema = LecturerSchema()
login_schema = LoginSchema()
course_schema = CourseSchema()
timetable_schema = TimetableSchema()

# Helper functions
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def get_face_encoding(image):
    face_locations = face_recognition.face_locations(image)
    if not face_locations:
        return None
    face_encodings = face_recognition.face_encodings(image, face_locations)
    if not face_encodings:
        return None
    return face_encodings[0].tolist()

def compare_faces(known_encoding, unknown_encoding):
    return face_recognition.compare_faces([known_encoding], unknown_encoding)[0]

# Routes
@app.route('/api/admin/register_student', methods=['POST'])
@jwt_required()
def register_student():
    try:
        data = request.form
        errors = student_schema.validate(data)
        if errors:
            return jsonify({"error": errors}), 400

        files = request.files.getlist('files')
        if not files:
            return jsonify({"error": "No files provided"}), 400

        face_encodings = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                image = face_recognition.load_image_file(filepath)
                encoding = get_face_encoding(image)
                if encoding:
                    face_encodings.append(encoding)

                os.remove(filepath)

        if not face_encodings:
            return jsonify({"error": "No valid face found in the images"}), 400

        new_student = Student(
            student_id=data['student_id'],
            name=data['name'],
            email=data['email'],
            face_encodings=face_encodings
        )
        db.session.add(new_student)
        db.session.commit()

        return jsonify({"message": "Student registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error registering student: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/student/login', methods=['POST'])
def student_login():
    try:
        data = request.json
        image_data = base64.b64decode(data['image'].split(',')[1])
        image = face_recognition.load_image_file(io.BytesIO(image_data))
        
        unknown_encoding = get_face_encoding(image)
        if unknown_encoding is None:
            return jsonify({"error": "No face detected in the image"}), 400
        
        students = Student.query.all()
        for student in students:
            for known_encoding in student.face_encodings:
                if compare_faces(known_encoding, unknown_encoding):
                    session = Session(student_id=student.student_id, course_id=data['course_id'])
                    db.session.add(session)
                    db.session.commit()

                    qr_data = f"http://localhost:3000/end-session/{session.session_id}"
                    qr_code = generate_qr_code(qr_data)

                    return jsonify({
                        "message": "Login successful",
                        "student_id": student.student_id,
                        "session_id": session.session_id,
                        "qr_code": qr_code
                    }), 200
        
        return jsonify({"error": "No matching student found"}), 401
    except Exception as e:
        logger.error(f"Error during student login: {e}")
        return jsonify({"error": "Login failed"}), 500

@app.route('/api/student/end_session/<int:session_id>', methods=['POST'])
def end_student_session(session_id):
    try:
        data = request.json
        image_data = base64.b64decode(data['image'].split(',')[1])
        image = face_recognition.load_image_file(io.BytesIO(image_data))
        
        unknown_encoding = get_face_encoding(image)
        if unknown_encoding is None:
            return jsonify({"error": "No face detected in the image"}), 400
        
        session = Session.query.get(session_id)
        if not session or session.status != 'active':
            return jsonify({"error": "Invalid session or session already ended"}), 400
        
        student = Student.query.get(session.student_id)
        for known_encoding in student.face_encodings:
            if compare_faces(known_encoding, unknown_encoding):
                session.end_time = datetime.utcnow()
                session.status = 'ended'
                db.session.commit()
                return jsonify({"message": "Session ended successfully"}), 200
        
        return jsonify({"error": "Face does not match the session's student"}), 401
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        return jsonify({"error": "Failed to end session"}), 500

@app.route('/api/lecturer/login', methods=['POST'])
def lecturer_login():
    try:
        data = request.json
        errors = login_schema.validate(data)
        if errors:
            return jsonify({"error": errors}), 400
        
        lecturer = Lecturer.query.filter_by(email=data['email']).first()
        
        if lecturer and check_password_hash(lecturer.password, data['password']):
            access_token = create_access_token(identity=lecturer.lecturer_id)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        logger.error(f"Error during lecturer login: {e}")
        return jsonify({"error": "Login failed"}), 500

@app.route('/api/lecturer/end_all_sessions', methods=['POST'])
@jwt_required()
def end_all_sessions():
    try:
        data = request.json
        course_id = data['course_id']
        
        active_sessions = Session.query.filter_by(course_id=course_id, status='active').all()
        for session in active_sessions:
            session.end_time = datetime.utcnow()
            session.status = 'ended'
        
        db.session.commit()
        return jsonify({"message": f"Ended {len(active_sessions)} active sessions"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error ending all sessions: {e}")
        return jsonify({"error": "Failed to end sessions"}), 500

@app.route('/api/lecturer/current_attendance', methods=['GET'])
@jwt_required()
def get_current_attendance():
    try:
        course_id = request.args.get('course_id')
        active_sessions = Session.query.filter_by(course_id=course_id, status='active').all()
        
        attendance = [{
            "student_id": session.student_id,
            "start_time": session.start_time.isoformat()
        } for session in active_sessions]
        
        return jsonify(attendance), 200
    except Exception as e:
        logger.error(f"Error getting current attendance: {e}")
        return jsonify({"error": "Failed to get current attendance"}), 500

@app.route('/api/admin/student_history', methods=['GET'])
@jwt_required()
def get_student_history():
    try:
        student_id = request.args.get('student_id')
        sessions = Session.query.filter_by(student_id=student_id).order_by(Session.start_time.desc()).all()
        
        history = [{
            "session_id": session.session_id,
            "course_id": session.course_id,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "status": session.status
        } for session in sessions]
        
        return jsonify(history), 200
    except Exception as e:
        logger.error(f"Error getting student history: {e}")
        return jsonify({"error": "Failed to get student history"}), 500

@app.route('/api/admin/add_course', methods=['POST'])
@jwt_required()
def add_course():
    try:
        data = request.json
        errors = course_schema.validate(data)
        if errors:
            return jsonify({"error": errors}), 400

        new_course = Course(course_name=data['course_name'], lecturer_id=data['lecturer_id'])
        db.session.add(new_course)
        db.session.commit()
        return jsonify({"message": "Course added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding course: {e}")
        return jsonify({"error": "Failed to add course"}), 500

@app.route('/api/admin/add_timetable', methods=['POST'])
@jwt_required()
def add_timetable():
    try:
        data = request.json
        errors = timetable_schema.validate(data)
        if errors:
            return jsonify({"error": errors}), 400

        new_timetable = Timetable(
            course_id=data['course_id'],
            day_of_week=data['day_of_week'],
            start_time=datetime.strptime(data['start_time'], '%H:%M').time(),
            end_time=datetime.strptime(data['end_time'], '%H:%M').time()
        )
        db.session.add(new_timetable)
        db.session.commit()
        return jsonify({"message": "Timetable entry added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding timetable entry: {e}")
        return jsonify({"error": "Failed to add timetable entry"}), 500

@app.route('/api/admin/register_lecturer', methods=['POST'])
@jwt_required()
def register_lecturer():
    try:
        data = request.json
        errors = lecturer_schema.validate(data)
        if errors:
            return jsonify({"error": errors}), 400

        hashed_password = generate_password_hash(data['password'])
        new_lecturer = Lecturer(
            name=data['name'],
            email=data['email'],
            password=hashed_password
        )
        db.session.add(new_lecturer)
        db.session.commit()
        return jsonify({"message": "Lecturer registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error registering lecturer: {e}")
        return jsonify({"error": "Failed to register lecturer"}), 500

# Background job for ending expired sessions
def end_expired_sessions():
    with app.app_context():
        now = datetime.utcnow()
        active_sessions = Session.query.filter_by(status='active').all()
        for session in active_sessions:
            timetable = Timetable.query.filter_by(course_id=session.course_id).first()
            if timetable:
                session_end_time = datetime.combine(session.start_time.date(), timetable.end_time)
                if now > session_end_time:
                    session.end_time = session_end_time
                    session.status = 'ended'
        db.session.commit()

# Initialize and start the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(end_expired_sessions, CronTrigger(minute='*/5'))
scheduler.start()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)