from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, distinct
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, time
import base64
import io
import qrcode
from io import BytesIO
import cv2
import numpy as np
import logging
import os
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


# Import the FaceRecognition class
from claude_face_recognition import FaceRecognition

app = Flask(__name__)
# CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173", "allow_headers": ["Content-Type", "Authorization"]}})

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://laravel_user:laravel_user@localhost/attendance_system_v1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-this'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1, minutes=30)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TEMP_IMAGE_FOLDER'] = os.path.abspath('temp_images')
app.config['MAX_TEMP_IMAGES'] = 5

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Initialize FaceRecognition
face_recognition = FaceRecognition.get_instance()

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
    course = db.relationship('Course', backref='timetable_entries')

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

# Routes
@app.route('/api/admin/register', methods=['POST'])
def register_admin():
    try:
        data = request.json
        errors = lecturer_schema.validate(data)
        if errors:
            return jsonify({"error": errors}), 400

        hashed_password = generate_password_hash(data['password'])
        new_admin = Admin(
            name=data['name'],
            email=data['email'],
            password=hashed_password
        )
        db.session.add(new_admin)
        db.session.commit()
        return jsonify({"message": "Admin registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error registering admin: {e}")
        return jsonify({"error": "Failed to register admin"}), 500

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.json
        errors = login_schema.validate(data)
        if errors:
            return jsonify({"error": errors}), 400
        
        admin = Admin.query.filter_by(email=data['email']).first()
        
        if admin and check_password_hash(admin.password, data['password']):
            access_token = create_access_token(identity=admin.admin_id,additional_claims={
            'exp': datetime.utcnow() + timedelta(hours=1, minutes=30)
        })
            return jsonify({
                "id": admin.admin_id,
                "name": admin.name,
                "role": "admin",
                "access_token": access_token
            }), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        logger.error(f"Error during admin login: {e}")
        return jsonify({"error": "Login failed"}), 500

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

        face_embeddings = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                image = cv2.imread(filepath)
                face_embedding = face_recognition.register_face(image)
                if face_embedding:
                    face_embeddings.extend(face_embedding)

                os.remove(filepath)

        if not face_embeddings:
            return jsonify({"error": "No valid face found in the images"}), 400

        new_student = Student(
            student_id=data['student_id'],
            name=data['name'],
            email=data['email'],
            face_encodings=face_embeddings
        )
        db.session.add(new_student)
        db.session.commit()

        return jsonify({"message": "Student registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error registering student: {e}")
        return jsonify({"error": str(e)}), 500

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from datetime import datetime, timedelta

@app.route('/api/admin/dashboard', methods=['GET'])
@jwt_required()
def get_admin_dashboard():
    try:
        # Fetch total counts
        total_students = Student.query.count()
        total_lecturers = Lecturer.query.count()
        total_courses = Course.query.count()

        # Fetch recent students
        recent_students = db.session.query(
            Student,
            func.count(Session.session_id).label('total_sessions')
        ).outerjoin(Session).group_by(Student).order_by(Student.created_at.desc()).limit(5).all()

        # Fetch top lecturers
        top_lecturers = db.session.query(
            Lecturer,
            func.count(Course.course_id).label('courses_count')
        ).outerjoin(Course).group_by(Lecturer).order_by(func.count(Course.course_id).desc()).limit(5).all()

        # Fetch popular courses
        popular_courses = db.session.query(
            Course,
            Lecturer.name.label('lecturer_name'),
            func.count(distinct(Session.student_id)).label('students_count')
        ).join(Lecturer).outerjoin(Session).group_by(Course).order_by(func.count(distinct(Session.student_id)).desc()).limit(5).all()

        # Fetch attendance statistics for the past week
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        attendance_stats = db.session.query(
            func.date(Session.start_time).label('date'),
            func.count(Session.session_id).label('count')
        ).filter(Session.start_time.between(start_date, end_date)
        ).group_by(func.date(Session.start_time)
        ).order_by(func.date(Session.start_time)).all()

        # Fetch course distribution
        course_distribution = db.session.query(
            Course.course_name,
            func.count(distinct(Session.student_id)).label('students_count')
        ).outerjoin(Session).group_by(Course).order_by(func.count(distinct(Session.student_id)).desc()).limit(5).all()

        dashboard_data = {
            'totalStudents': total_students,
            'totalLecturers': total_lecturers,
            'totalCourses': total_courses,
            'recentStudents': [
                {
                    'student_id': student.Student.student_id,
                    'name': student.Student.name,
                    'email': student.Student.email,
                    'total_sessions': student.total_sessions
                } for student in recent_students
            ],
            'topLecturers': [
                {
                    'lecturer_id': lecturer.Lecturer.lecturer_id,
                    'name': lecturer.Lecturer.name,
                    'email': lecturer.Lecturer.email,
                    'courses_count': lecturer.courses_count
                } for lecturer in top_lecturers
            ],
            'popularCourses': [
                {
                    'course_id': course.Course.course_id,
                    'course_name': course.Course.course_name,
                    'lecturer_name': course.lecturer_name,
                    'students_count': course.students_count
                } for course in popular_courses
            ],
            'attendanceStats': {
                'labels': [stat.date.strftime('%Y-%m-%d') for stat in attendance_stats],
                'datasets': [{
                    'label': 'Daily Attendance',
                    'data': [stat.count for stat in attendance_stats],
                    'backgroundColor': 'rgba(75, 192, 192, 0.6)',
                }]
            },
            'courseDistribution': {
                'labels': [course.course_name for course in course_distribution],
                'datasets': [{
                    'label': 'Students per Course',
                    'data': [course.students_count for course in course_distribution],
                    'backgroundColor': [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)',
                    ],
                }]
            }
        }

        return jsonify(dashboard_data), 200
    except Exception as e:
        print(f"Error in admin dashboard: {str(e)}")
        return jsonify({"error": "Failed to fetch admin dashboard data"}), 500

# Add these new endpoints for the admin actions

@app.route('/api/admin/register_lecturer', methods=['POST'])
@jwt_required()
def admin_register_lecturer():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not all([name, email, password]):
            return jsonify({"error": "Missing required fields"}), 400

        hashed_password = generate_password_hash(password)
        new_lecturer = Lecturer(name=name, email=email, password=hashed_password)
        db.session.add(new_lecturer)
        db.session.commit()

        return jsonify({"message": "Lecturer registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error registering lecturer: {str(e)}")
        return jsonify({"error": "Failed to register lecturer"}), 500

@app.route('/api/admin/add_course', methods=['POST'])
@jwt_required()
def admin_add_course():
    try:
        data = request.json
        course_name = data.get('course_name')
        lecturer_id = data.get('lecturer_id')

        if not all([course_name, lecturer_id]):
            return jsonify({"error": "Missing required fields"}), 400

        new_course = Course(course_name=course_name, lecturer_id=lecturer_id)
        db.session.add(new_course)
        db.session.commit()

        return jsonify({"message": "Course added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error adding course: {str(e)}")
        return jsonify({"error": "Failed to add course"}), 500

@app.route('/api/admin/add_timetable', methods=['POST'])
@jwt_required()
def admin_add_timetable():
    try:
        data = request.json
        course_id = data.get('course_id')
        day = data.get('day')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if not all([course_id, day, start_time, end_time]):
            return jsonify({"error": "Missing required fields"}), 400

        new_timetable = Timetable(
            course_id=course_id,
            day_of_week=day,
            start_time=datetime.strptime(start_time, '%H:%M').time(),
            end_time=datetime.strptime(end_time, '%H:%M').time()
        )
        db.session.add(new_timetable)
        db.session.commit()

        return jsonify({"message": "Timetable entry added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error adding timetable entry: {str(e)}")
        return jsonify({"error": "Failed to add timetable entry"}), 500

@app.route('/api/student/login', methods=['POST'])
def student_login():
    try:
        data = request.json
        image_data = base64.b64decode(data['image'].split(',')[1])
        image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        
        face_embedding = face_recognition.get_face_embedding(image)
        if face_embedding is None:
            return jsonify({"error": "No face detected in the image"}), 400
        
        students = Student.query.all()
        for student in students:
            if face_recognition.recognize_face(face_embedding, student.face_encodings):
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
        image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        
        face_embedding = face_recognition.get_face_embedding(image)
        if face_embedding is None:
            return jsonify({"error": "No face detected in the image"}), 400
        
        session = Session.query.get(session_id)
        if not session or session.status != 'active':
            return jsonify({"error": "Invalid session or session already ended"}), 400
        
        student = Student.query.get(session.student_id)
        if face_recognition.recognize_face(face_embedding, student.face_encodings):
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
            access_token = create_access_token(identity=lecturer.lecturer_id,additional_claims={
            'exp': datetime.utcnow() + timedelta(hours=1, minutes=30)
        })
            return jsonify({
                "id": lecturer.lecturer_id,
                "name": lecturer.name,
                "role": "lecturer",
                "access_token": access_token
                }), 200
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
            "start_time": session.start_time.isoformat(),
            "end_time": (session.start_time + timedelta(hours=1, minutes=30)).isoformat()
        } for session in active_sessions]
        
        return jsonify(attendance), 200
    except Exception as e:
        logger.error(f"Error getting current attendance: {e}")
        return jsonify({"error": "Failed to get current attendance"}), 500

@app.route('/api/teacher/dashboard', methods=['GET'])
@jwt_required()
def get_teacher_dashboard():
    teacher_id = get_jwt_identity()
    
    # Fetch active students
    active_students = db.session.query(Student).join(Session).join(Course).filter(
        Course.lecturer_id == teacher_id,
        Session.status == 'active'
    ).all()

    # Fetch courses and student counts
    courses = db.session.query(
        Course.course_id,
        Course.course_name,
        func.count(distinct(Session.student_id)).label('active_students'),
        func.count(distinct(Student.student_id)).label('total_students')
    ).outerjoin(Session, Session.course_id == Course.course_id)\
     .outerjoin(Student, Student.student_id == Session.student_id)\
     .filter(Course.lecturer_id == teacher_id)\
     .group_by(Course.course_id)\
     .all()

    # Fetch timetable
    timetable_entries = db.session.query(Timetable, Course.course_name)\
        .join(Course, Course.course_id == Timetable.course_id)\
        .filter(Course.lecturer_id == teacher_id)\
        .all()

    # Fetch attendance statistics for the past week
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    attendance_stats = db.session.query(
        func.date(Session.start_time).label('date'),
        func.count(Session.session_id).label('count')
    ).join(Course, Course.course_id == Session.course_id)\
     .filter(
        Course.lecturer_id == teacher_id,
        Session.start_time.between(start_date, end_date)
    ).group_by(func.date(Session.start_time))\
     .order_by(func.date(Session.start_time))\
     .all()

    return jsonify({
        'activeStudents': [
            {
                'student_id': student.student_id,
                'name': student.name,
                'email': student.email,
                'status': 'active'
            } for student in active_students
        ],
        'courses': [
            {
                'course_id': course.course_id,
                'course_name': course.course_name,
                'active_students': course.active_students,
                'total_students': course.total_students
            } for course in courses
        ],
        'timetable': [
            {
                'day': entry.Timetable.day_of_week,
                'start_time': entry.Timetable.start_time.strftime('%H:%M'),
                'end_time': entry.Timetable.end_time.strftime('%H:%M'),
                'course_name': entry.course_name
            } for entry in timetable_entries
        ],
        'attendanceStats': {
            'labels': [stat.date.strftime('%Y-%m-%d') for stat in attendance_stats],
            'datasets': [{
                'label': 'Daily Attendance',
                'data': [stat.count for stat in attendance_stats],
                'backgroundColor': 'rgba(75, 192, 192, 0.6)',
            }]
        }
    }), 200

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


# data entry into the timetable table
@app.route('/api/generate_timetable/<int:lecturer_id>', methods=['GET'])
def generate_timetable(lecturer_id):
    courses = [
        {"course_name": "IST 2103 Information System Security and Risk Management", "day_of_week": "Monday", "start_time": "14:00", "end_time": "16:00"},
        {"course_name": "IST 2103 Information System Security and Risk Management", "day_of_week": "Friday", "start_time": "14:00", "end_time": "16:00"},
    ]

    for course in courses:
        # Check if the course already exists
        existing_course = Course.query.filter_by(course_name=course['course_name'], lecturer_id=lecturer_id).first()
        
        if not existing_course:
            # Create a new course
            new_course = Course(course_name=course['course_name'], lecturer_id=lecturer_id)
            db.session.add(new_course)
            db.session.commit()
            course_id = new_course.course_id
        else:
            course_id = existing_course.course_id
        
        # Add timetable entry
        new_timetable_entry = Timetable(
            course_id=course_id,
            day_of_week=course['day_of_week'],
            start_time=datetime.strptime(course['start_time'], '%H:%M').time(),
            end_time=datetime.strptime(course['end_time'], '%H:%M').time()
        )
        db.session.add(new_timetable_entry)

    db.session.commit()
    return jsonify({"message": "Timetable generated successfully"}), 201

# Background job for ending expired sessions
def end_expired_sessions():
    with app.app_context():
        now = datetime.utcnow()
        active_sessions = Session.query.filter_by(status='active').all()
        for session in active_sessions:
            timetable = Timetable.query.filter_by(course_id=session.course_id).first()
            if timetable:
                session_end_time = datetime.combine(session.start_time.date(), timetable.end_time)
                # Add 1 hour and 30 minutes to the session end time
                extended_end_time = session_end_time + timedelta(hours=1, minutes=30)
                if now > extended_end_time:
                    session.end_time = extended_end_time
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