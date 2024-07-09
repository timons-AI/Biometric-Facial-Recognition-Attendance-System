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
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, distinct, case
from pytz import timezone


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
    password = db.Column(db.String(255), nullable=False)
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
    password = fields.Str(required=True, validate=validate.Length(min=6))

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
        files = request.files.getlist('files')

        # Validate input data
        required_fields = ['student_id', 'name', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Validate files
        if not files:
            return jsonify({"error": "No files provided"}), 400

        face_embeddings = []
        face_recognition = FaceRecognition.get_instance()

        for file in files:
            if file and allowed_file(file.filename):
                try:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    logger.info(f"Processing image: {filename}")
                    image = cv2.imread(filepath)
                    
                    if image is None:
                        logger.warning(f"Could not read image: {filename}")
                        continue

                    faces = face_recognition.detect_faces(image)
                    
                    if not faces:
                        logger.warning(f"No faces detected in image: {filename}")
                        continue

                    for face in faces:
                        try:
                            aligned_face = face_recognition.align_face(image, face)
                            face_embedding = face_recognition.get_face_embedding(aligned_face)
                            
                            if face_embedding is not None and len(face_embedding) > 0:
                                face_embeddings.append(face_embedding.tolist())
                                logger.info(f"Face embedding added. Total embeddings: {len(face_embeddings)}")
                            else:
                                logger.warning(f"Invalid face embedding for face in {filename}")
                        except Exception as e:
                            logger.error(f"Error processing face in {filename}: {str(e)}")

                except Exception as e:
                    logger.error(f"Error processing file {filename}: {str(e)}")
                finally:
                    if os.path.exists(filepath):
                        os.remove(filepath)

        if not face_embeddings:
            return jsonify({"error": "No valid faces found in the uploaded images"}), 400

        # Create new student
        new_student = Student(
            student_id=data['student_id'],
            name=data['name'],
            email=data['email'],
            password=generate_password_hash(data['password']),
            face_encodings=face_embeddings
        )

        db.session.add(new_student)
        db.session.commit()

        return jsonify({"message": "Student registered successfully"}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error registering student: {str(e)}")
        return jsonify({"error": "An unexpected error occurred while registering the student"}), 500

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
    data = request.json
    email = data.get('email')
    password = data.get('password')

    student = Student.query.filter_by(email=email).first()
    
    if student and check_password_hash(student.password, password):
        access_token = create_access_token(identity=student.student_id)
        return jsonify({
            "message": "Login successful",
            "name": student.name,
            "student_id": student.student_id,
            "access_token": access_token
        }), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401

@app.route('/api/student/courses', methods=['GET'])
@jwt_required()
def get_student_courses():
    student_id = get_jwt_identity()
    # Fetch courses the student is enrolled in
    # courses = db.session.query(Course).join(Session).filter(Session.student_id == student_id).distinct().all()
    # Get normoral courses.
    courses = Course.query.all()
    return jsonify([
        {"id": course.course_id, "name": course.course_name}
        for course in courses
    ]), 200

@app.route('/api/student/start_session', methods=['POST'])
@jwt_required()
def start_student_session():
    try:
        student_id = get_jwt_identity()
        data = request.json
        course_id = data.get('course_id')
        image_data = data.get('image')

        if not course_id or not image_data:
            return jsonify({"error": "Missing course_id or image data"}), 400

        # Get current day and time in the correct time zone
        local_tz = timezone('Africa/Nairobi')  # Replace with your actual timezone
        current_datetime = datetime.now(local_tz)
        current_day = current_datetime.strftime('%A')

        # Check timetable
        timetable_entry = Timetable.query.filter_by(
            course_id=course_id,
            day_of_week=current_day
        ).first()

        if not timetable_entry:
            return jsonify({"error": "No class scheduled for this course today"}), 400

        # Convert naive time to aware datetime
        start_time = local_tz.localize(datetime.combine(current_datetime.date(), timetable_entry.start_time))
        end_time = local_tz.localize(datetime.combine(current_datetime.date(), timetable_entry.end_time))

        if end_time < start_time:  # Course spans midnight
            end_time += timedelta(days=1)

        if not (start_time <= current_datetime <= end_time):
            return jsonify({"error": "No class scheduled at this time"}), 400

        # Decode and process the image
        image_data = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        logger.info(f"Received image shape: {image.shape}")

        faces = face_recognition.detect_faces(image)
        logger.info(f"Detected faces: {len(faces)}")

        if not faces:
            # Save the problematic image for debugging
            cv2.imwrite('debug_image.jpg', image)
            return jsonify({"error": "No face detected in the image"}), 400

        aligned_face = face_recognition.align_face(image, faces[0])
        logger.info(f"Aligned face shape: {aligned_face.shape}")

        face_embedding = face_recognition.get_face_embedding(aligned_face)
        if face_embedding is None:
            return jsonify({"error": "Failed to get face embedding"}), 400
        
        # Verify the face matches the student
        student = Student.query.get(student_id)
        if not face_recognition.recognize_face(face_embedding, student.face_encodings):
            return jsonify({"error": "Face does not match the student's record"}), 401

        # Start the session
        session = Session(student_id=student_id, course_id=course_id)
        db.session.add(session)
        db.session.commit()

        # Generate QR code
        qr_data = f"http://localhost:3000/end-session/{session.session_id}"
        qr_code = generate_qr_code(qr_data)

        return jsonify({
            "message": "Session started successfully",
            "session_id": session.session_id,
            "qr_code": qr_code
        }), 200

    except Exception as e:
        logger.error(f"Error starting session: {e}", exc_info=True)
        return jsonify({"error": "Failed to start session"}), 500
           
@app.route('/api/student/end_session/<int:session_id>', methods=['POST'])
@jwt_required()
def end_student_session(session_id):
    try:
        student_id = get_jwt_identity()
        session = Session.query.get(session_id)
        
        if not session or session.student_id != student_id:
            return jsonify({"error": "Invalid session"}), 400
        
        if session.status != 'active':
            return jsonify({"error": "Session already ended"}), 400
        
        session.end_time = datetime.utcnow()
        session.status = 'ended'
        db.session.commit()
        
        return jsonify({"message": "Session ended successfully"}), 200
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        return jsonify({"error": "Failed to end session"}), 500


@app.route('/api/student/dashboard', methods=['GET'])
@jwt_required()
def get_student_dashboard():
    try:
        student_id = get_jwt_identity()
        
        # Fetch active session
        active_session = Session.query.filter_by(student_id=student_id, status='active').first()
        active_session_data = None
        if active_session:
            course = Course.query.get(active_session.course_id)
            lecturer = Lecturer.query.get(course.lecturer_id)
            qr_data = f"http://localhost:3000/end-session/{active_session.session_id}"
            qr_code = generate_qr_code(qr_data)
            active_session_data = {
                "session_id": active_session.session_id,
                "course_name": course.course_name,
                "lecturer_name": lecturer.name,
                "start_time": active_session.start_time.isoformat(),
                "end_time": (active_session.start_time + timedelta(hours=1, minutes=30)).isoformat(),
                "qr_code": qr_code
            }

        # Fetch attendance stats for the past 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        attendance_stats = db.session.query(
            func.date(Session.start_time).label('date'),
            func.count(Session.session_id).label('count')
        ).filter(
            Session.student_id == student_id,
            Session.start_time.between(start_date, end_date)
        ).group_by(func.date(Session.start_time)
        ).order_by(func.date(Session.start_time)).all()

        # Fetch timetable for the current week
        current_day = datetime.now().weekday()
        week_start = datetime.now() - timedelta(days=current_day)
        week_end = week_start + timedelta(days=6)

        timetable = db.session.query(
            Timetable.day_of_week,
            Course.course_name,
            Timetable.start_time,
            Timetable.end_time,
            Lecturer.name.label('lecturer_name')
        ).join(Course, Course.course_id == Timetable.course_id
        ).join(Lecturer, Lecturer.lecturer_id == Course.lecturer_id
        ).filter(
            case(
                {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6},
                value=Timetable.day_of_week
            ).between(current_day, current_day + 6)
        ).order_by(
            case(
                {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6},
                value=Timetable.day_of_week
            ),
            Timetable.start_time
        ).all()

        # Group timetable by day
        timetable_by_day = {}
        for entry in timetable:
            if entry.day_of_week not in timetable_by_day:
                timetable_by_day[entry.day_of_week] = []
            timetable_by_day[entry.day_of_week].append({
                "course_name": entry.course_name,
                "start_time": entry.start_time.strftime('%H:%M'),
                "end_time": entry.end_time.strftime('%H:%M'),
                "lecturer_name": entry.lecturer_name
            })

        # Calculate total attendance and courses
        total_attendance = Session.query.filter_by(student_id=student_id).count()
        total_courses = db.session.query(func.count(distinct(Session.course_id))).filter_by(student_id=student_id).scalar()

        dashboard_data = {
            "activeSession": active_session_data,
            "attendanceStats": {
                "labels": [stat.date.strftime('%Y-%m-%d') for stat in attendance_stats],
                "datasets": [{
                    "label": 'Attendance',
                    "data": [stat.count for stat in attendance_stats],
                    "borderColor": 'rgb(75, 192, 192)',
                    "backgroundColor": 'rgba(75, 192, 192, 0.5)',
                }]
            },
            "timetable": [
                {"day": day, "courses": courses}
                for day, courses in timetable_by_day.items()
            ],
            "totalAttendance": total_attendance,
            "totalCourses": total_courses,
            "currentDay": datetime.now().strftime('%A'),
            "currentTimestamp": datetime.now().isoformat()
        }

        return jsonify(dashboard_data), 200
    except Exception as e:
        logger.error(f"Error in student dashboard: {str(e)}")
        return jsonify({"error": "Failed to fetch student dashboard data"}), 500

# Other routes and functions remain the same

   
@app.route('/api/timetable/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_timetable(course_id):
    timetable_entries = Timetable.query.filter_by(course_id=course_id).all()
    
    timetable = [{
        "day": entry.day_of_week,
        "start_time": entry.start_time.strftime('%H:%M'),
        "end_time": entry.end_time.strftime('%H:%M')
    } for entry in timetable_entries]
    
    return jsonify(timetable), 200
     
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

@app.route('/api/student/active_session', methods=['GET'])
@jwt_required()
def get_active_session():
    try:
        student_id = get_jwt_identity()
        active_session = Session.query.filter_by(student_id=student_id, status='active').first()
        
        if active_session:
            course = Course.query.get(active_session.course_id)
            qr_data = f"http://localhost:5173/end-session/{active_session.session_id}"
            qr_code = generate_qr_code(qr_data)
            
            return jsonify({
                "session_id": active_session.session_id,
                "course_name": course.course_name,
                "start_time": active_session.start_time.isoformat(),
                "qr_code": qr_code
            }), 200
        else:
            return jsonify(None), 200
    except Exception as e:
        logger.error(f"Error fetching active session: {e}")
        return jsonify({"error": "Failed to fetch active session"}), 500

from datetime import datetime, timedelta
from pytz import timezone

@app.route('/api/student/active_courses', methods=['GET'])
@jwt_required()
def get_active_courses():
    try:
        student_id = get_jwt_identity()
       
        # Get current day and time in the correct time zone
        local_tz = timezone('Africa/Nairobi')  # Replace with your actual timezone
        current_datetime = datetime.now(local_tz)
        current_day = current_datetime.strftime('%A')

        # Query for active courses
        active_courses = db.session.query(Course).join(Timetable).filter(
            Timetable.day_of_week == current_day
        ).all()

        # Filter courses manually to handle courses that span midnight
        result = []
        for course in active_courses:
            timetable = course.timetable_entries[0]  # Assuming one timetable entry per course
            
            # Convert naive time to aware datetime
            start_time = local_tz.localize(datetime.combine(current_datetime.date(), timetable.start_time))
            end_time = local_tz.localize(datetime.combine(current_datetime.date(), timetable.end_time))
            
            if end_time < start_time:  # Course spans midnight
                end_time += timedelta(days=1)
            
            if start_time <= current_datetime <= end_time:
                result.append({"id": course.course_id, "name": course.course_name})

        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error fetching active courses: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch active courses"}), 500
        
# data entry into the timetable table
@app.route('/api/generate_timetable/<int:lecturer_id>', methods=['GET'])
def generate_timetable(lecturer_id):
    courses = [
        {"course_name": "IST 1334 Basic Mathematics", "day_of_week": "Tuesday", "start_time": "10:00", "end_time": "01:00"},
        {"course_name": "IST 2422 Emerging Trends in Information Technology", "day_of_week": "Tuesday", "start_time": "12:00", "end_time": "2:00"},
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