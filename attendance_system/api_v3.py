from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import string
from flask import current_app
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, time
from sqlalchemy import func, and_, or_, case
import os
from functools import wraps
from sqlalchemy import Enum
import enum
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
import logging
import cv2
import numpy as np
import traceback
import base64
from io import BytesIO
from PIL import Image
import random
from faker import Faker
import json
import re

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

fake = Faker()
# Import your face recognition module
from claude_face_recognition import FaceRecognition

app = Flask(__name__)
# CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization"]}})
CORS(app, resources={r"/api/*": {"origins": ["*","https://7384-129-205-1-137.ngrok-free.app","https://biometric-facial-recognition-attendance-system.vercel.app"], "allow_headers": ["Content-Type", "Authorization", "ngrok-skip-browser-warning"], "methods": ["GET", "POST", "PUT", "DELETE"]}})
# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://laravel_user:laravel_user@localhost/attendance_system_v2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-this'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1, minutes=30)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize FaceRecognition
face_recognition = FaceRecognition.get_instance()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student', 'lecturer', 'admin'
    is_approved = db.Column(db.Boolean, default=False)
    # created_at = db.Column(db.DateTime, default=datetime.now)
  
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_year.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'), nullable=False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'), nullable=False)
    face_encoding = db.Column(db.PickleType)

class Lecturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)

class DayOfWeek(enum.Enum):
    MONDAY = 'Monday'
    TUESDAY = 'Tuesday'
    WEDNESDAY = 'Wednesday'
    THURSDAY = 'Thursday'
    FRIDAY = 'Friday'
    SATURDAY = 'Saturday'
    SUNDAY = 'Sunday'

class AcademicYear(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(9), unique=True, nullable=False)  # e.g., "2023/2024"

class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_year.id'), nullable=False)
    name = db.Column(db.String(20), nullable=False)  # e.g., "Semester I"
    academic_year = db.relationship('AcademicYear', backref='semesters')

class College(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'), nullable=False)
    college = db.relationship('College', backref='courses')

class CourseUnit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    course = db.relationship('Course', backref='course_units')

class Timetable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'), nullable=False)
    course_unit_id = db.Column(db.Integer, db.ForeignKey('course_unit.id'), nullable=False)
    day = db.Column(Enum(DayOfWeek), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    room = db.Column(db.String(50), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    semester = db.relationship('Semester', backref='timetables')
    course_unit = db.relationship('CourseUnit', backref='timetables')
    lecturer = db.relationship('User', backref=db.backref('timetables', lazy='dynamic'))

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timetable_id = db.Column(db.Integer, db.ForeignKey('timetable.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in_time = db.Column(db.DateTime, nullable=False)
    check_out_time = db.Column(db.DateTime)
    student = db.relationship('User', backref='attendances')
    timetable = db.relationship('Timetable', backref='attendances')

# Helper functions
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if user.role != 'admin':
            return jsonify({"msg": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


def load_existing_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def save_data(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def create_base_data():
    with app.app_context():
        # Create Academic Years if they don't exist
        if AcademicYear.query.count() == 0:
            years = ["2023/2024", "2024/2025", "2025/2026"]
            for year in years:
                db.session.add(AcademicYear(year=year))

        # Create Colleges if they don't exist
        if College.query.count() == 0:
            colleges = ["College of Engineering", "College of Sciences", "College of Business", "College of Arts and Humanities"]
            for college_name in colleges:
                db.session.add(College(name=college_name))

        # Create Semesters if they don't exist
        if Semester.query.count() == 0:
            semesters = ["Semester I", "Semester II", "Semester III"]
            for semester_name in semesters:
                db.session.add(Semester(name=semester_name, academic_year_id=1))  # Assuming first academic year

        # Create Courses if they don't exist
        if Course.query.count() == 0:
            courses = [
                {"code": "CS101", "name": "Introduction to Computer Science"},
                {"code": "MATH201", "name": "Advanced Mathematics"},
                {"code": "BUS301", "name": "Business Management"},
                {"code": "ART101", "name": "Introduction to Fine Arts"}
            ]
            for course in courses:
                db.session.add(Course(code=course['code'], name=course['name'], college_id=1))  # Assuming first college

        # Create Course Units if they don't exist
        if CourseUnit.query.count() == 0:
            course_units = [
                {"code": "CS101-1", "name": "Programming Basics", "course_id": 1},
                {"code": "MATH201-1", "name": "Calculus", "course_id": 2},
                {"code": "BUS301-1", "name": "Marketing", "course_id": 3},
                {"code": "ART101-1", "name": "Drawing Techniques", "course_id": 4}
            ]
            for unit in course_units:
                db.session.add(CourseUnit(code=unit['code'], name=unit['name'], course_id=unit['course_id']))

        db.session.commit()
        print("Base data created successfully.")

def generate_unique_email(used_emails):
    while True:
        email = fake.email()
        if email not in used_emails:
            used_emails.add(email)
            return email

def get_next_student_id():
    max_id = db.session.query(func.max(Student.student_id)).scalar()
    if max_id:
        # Extract the numeric part and increment
        next_id = int(max_id[3:]) + 1
    else:
        next_id = 100001
    return f"STU{next_id}"

def get_next_course_code():
    max_code = db.session.query(func.max(Course.code)).scalar()
    if max_code:
        # Extract the numeric part if it exists
        match = re.search(r'\d+', max_code)
        if match:
            next_num = int(match.group()) + 1
        else:
            next_num = 1001
    else:
        next_num = 1001
    
    # Keep generating codes until we find an unused one
    while True:
        new_code = f"CRS{next_num:04d}"
        if not Course.query.filter_by(code=new_code).first():
            return new_code
        next_num += 1

def augment_existing_data(
    num_new_students=100,
    num_new_lecturers=10,
    num_new_courses=5,
    start_date=datetime(2024, 6, 1),
    end_date=datetime(2024, 12, 31)
):
    with current_app.app_context():
        # First, ensure base data exists
        create_base_data()

        used_emails = set(user.email for user in User.query.all())
        credentials = []

        # Generate new students
        new_students = []
        for i in range(num_new_students):
            email = generate_unique_email(used_emails)
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            user = User(email=email, role='student', is_approved=True)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()  # This assigns an id to the user

            student = Student(
                user_id=user.id,
                student_id=get_next_student_id(),
                name=fake.name(),
                academic_year_id=random.choice(AcademicYear.query.all()).id,
                course_id=random.choice(Course.query.all()).id,
                college_id=random.choice(College.query.all()).id,
                semester_id=random.choice(Semester.query.all()).id,
                face_encoding=None
            )
            new_students.append(student)
            db.session.add(student)
            credentials.append({"email": email, "password": password, "role": "student"})

        # Generate new lecturers
        new_lecturers = []
        for i in range(num_new_lecturers):
            email = generate_unique_email(used_emails)
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            user = User(email=email, role='lecturer', is_approved=True)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            lecturer = Lecturer(
                user_id=user.id,
                name=fake.name()
            )
            new_lecturers.append(lecturer)
            db.session.add(lecturer)
            credentials.append({"email": email, "password": password, "role": "lecturer"})

        # Generate new courses
        new_courses = []
        for i in range(num_new_courses):
            course = Course(
                code=get_next_course_code(),
                name=fake.catch_phrase(),
                college_id=random.choice(College.query.all()).id
            )
            new_courses.append(course)
            db.session.add(course)

        db.session.flush()  # This assigns ids to all new records

        # Generate new timetable entries
        days = list(DayOfWeek)
        new_timetable_entries = []
        for course in new_courses:
            num_sessions = random.randint(1, 3)
            course_lecturer = random.choice(new_lecturers + list(Lecturer.query.all()))
            course_days = random.sample(days, num_sessions)
            for day in course_days:
                timetable_entry = Timetable(
                    semester_id=random.choice(Semester.query.all()).id,
                    course_unit_id=random.choice(CourseUnit.query.all()).id,
                    day=day,
                    start_time=time(hour=random.choice([9, 11, 14, 16])),
                    end_time=time(hour=random.choice([11, 13, 16, 18])),
                    room=f"Room {random.randint(100, 500)}",
                    lecturer_id=course_lecturer.user_id
                )
                new_timetable_entries.append(timetable_entry)
                db.session.add(timetable_entry)

        db.session.flush()

        # Generate new attendance records
        new_attendance_records = []
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Monday to Friday
                for entry in new_timetable_entries + list(Timetable.query.all()):
                    if entry.day.value == current_date.strftime('%A'):
                        for student in random.sample(new_students + list(Student.query.all()), k=random.randint(1, 20)):
                            check_in_time = datetime.combine(current_date, entry.start_time) + timedelta(minutes=random.randint(0, 15))
                            check_out_time = datetime.combine(current_date, entry.end_time) - timedelta(minutes=random.randint(0, 15))
                            attendance = Attendance(
                                student_id=student.user_id,
                                timetable_id=entry.id,
                                date=current_date.date(),
                                check_in_time=check_in_time,
                                check_out_time=check_out_time
                            )
                            new_attendance_records.append(attendance)
                            db.session.add(attendance)
            current_date += timedelta(days=1)

        try:
            db.session.commit()
            print(f"Added {len(new_students)} new students")
            print(f"Added {len(new_lecturers)} new lecturers")
            print(f"Added {len(new_courses)} new courses")
            print(f"Added {len(new_timetable_entries)} new timetable entries")
            print(f"Added {len(new_attendance_records)} new attendance records")
            print("Data successfully added to the database.")

            # Save credentials to a JSON file
            with open('login_credentials.json', 'w') as f:
                json.dump(credentials, f, indent=2)
            print("Login credentials saved to login_credentials.json")

        except Exception as e:
            db.session.rollback()
            print(f"Error occurred while adding data to the database: {str(e)}")


@app.route('/api/register', methods=['POST'])
def register():
    logger.debug(f"Form data: {request.form}")
    logger.debug(f"Files: {request.files}")

    try:
        data = request.form.to_dict()
        
        # Check for required fields
        required_fields = ['email', 'password', 'name', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({"msg": f"{field.capitalize()} is required"}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({"msg": "Email already registered"}), 400

        user = User(email=data['email'], role=data['role'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()

        if data['role'] == 'student':
            student_fields = ['student_id', 'academic_year_id', 'course_id', 'college_id', 'semester_id']
            for field in student_fields:
                if field not in data:
                    return jsonify({"msg": f"{field.replace('_', ' ').capitalize()} is required"}), 400

            student = Student(
                user_id=user.id,
                student_id=data['student_id'],
                name=data['name'],
                academic_year_id=int(data['academic_year_id']),
                course_id=int(data['course_id']),
                college_id=int(data['college_id']),
                semester_id=int(data['semester_id'])
            )
            
            face_images = []
            for key, file in request.files.items():
                if file and allowed_file(file.filename):
                    file_data = file.read()
                    nparr = np.frombuffer(file_data, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    face_images.append(img)

            if not face_images:
                return jsonify({"msg": "At least one facial image is required"}), 400
            
            face_encodings = []
            face_recognition = FaceRecognition.get_instance()
            for image in face_images:
                faces = face_recognition.detect_faces(image)
                if faces:
                    aligned_face = face_recognition.align_face(image, faces[0])
                    face_embedding = face_recognition.get_face_embedding(aligned_face)
                    
                    if face_embedding is not None:
                        face_encodings.append(face_embedding.tolist())
                    else:
                        logger.warning(f"Failed to get face embedding for one of the images")
                else:
                    logger.warning(f"No face detected in one of the images")

            if not face_encodings:
                return jsonify({"msg": "Failed to extract valid face encodings from any of the provided images"}), 400

            student.face_encoding = face_encodings
            db.session.add(student)

        elif data['role'] == 'lecturer':
            lecturer = Lecturer(user_id=user.id, name=data['name'])
            db.session.add(lecturer)
        elif data['role'] == 'admin':
            admin = Admin(user_id=user.id, name=data['name'])
            db.session.add(admin)
        else:
            return jsonify({"msg": "Invalid role"}), 400

        try:
            db.session.commit()
            return jsonify({"msg": "User registered successfully. Awaiting approval."}), 201
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"IntegrityError: {str(e)}")
            logger.error(f"IntegrityError details: {e.orig}")
            return jsonify({"msg": f"Error registering user: {str(e)}"}), 500
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during database commit: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"msg": f"Error registering user: {str(e)}"}), 500

    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"msg": f"Unexpected error during registration: {str(e)}"}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        if not user.is_approved and user.role != 'admin':
            return jsonify({"msg": "Account not approved yet"}), 403
        
        # get the name of the user
        if user.role == 'student':
            student = Student.query.filter_by(user_id=user.id).first()
            name = student.name
        elif user.role == 'lecturer':
            lecturer = Lecturer.query.filter_by(user_id=user.id).first()
            name = lecturer.name
        else:
            admin = Admin.query.filter_by(user_id=user.id).first()
            name = admin.name
        # Include user information in the JWT payload
        additional_claims = {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "name": name
        }
        access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Invalid email or password"}), 401


@app.route('/api/register/admin', methods=['POST'])
# @jwt_required()
# @admin_required
def register_admin():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"msg": "Email already registered"}), 400
    
    user = User(email=data['email'], role='admin')
    user.set_password(data['password'])
    db.session.add(user)
    db.session.flush()

    admin = Admin(user_id=user.id, name=data['name'])
    db.session.add(admin)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"msg": "Error registering user"}), 500
    
    return jsonify({"msg": "Admin registered successfully."}), 201

@app.route('/api/admin/pending_registrations', methods=['GET'])
@jwt_required()
@admin_required
def get_pending_registrations():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Query for pending registrations of all user types
        pending_query = db.session.query(User).filter(
            User.is_approved == False
        ).order_by(User.id.desc())

        pending_users = pending_query.paginate(page=page, per_page=per_page, error_out=False)

        # Prepare the response data
        pending_data = []
        for user in pending_users.items:
            user_data = {
                "user_id": user.id,
                "email": user.email,
                "role": user.role,
                "name": None,
                "student_id": None,
                "academic_year_id": None,
                "course_id": None,
                "college_id": None,
                "semester_id": None
            }

            if user.role == 'student':
                student = Student.query.filter_by(user_id=user.id).first()
                if student:
                    user_data.update({
                        "name": student.name,
                        "student_id": student.student_id,
                        "academic_year_id": student.academic_year_id,
                        "course_id": student.course_id,
                        "college_id": student.college_id,
                        "semester_id": student.semester_id
                    })
            elif user.role == 'lecturer':
                lecturer = Lecturer.query.filter_by(user_id=user.id).first()
                if lecturer:
                    user_data["name"] = lecturer.name
            elif user.role == 'admin':
                admin = Admin.query.filter_by(user_id=user.id).first()
                if admin:
                    user_data["name"] = admin.name

            pending_data.append(user_data)

        return jsonify({
            "pending_registrations": pending_data,
            "total_count": pending_users.total,
            "pages": pending_users.pages,
            "current_page": page,
            "per_page": per_page
        }), 200

    except Exception as e:
        # Log the error
        app.logger.error(f"Error fetching pending registrations: {str(e)}")
        return jsonify({"msg": "An error occurred while fetching pending registrations"}), 500

# Update the approve and reject routes to handle all user types
@app.route('/api/admin/approve_user/<int:user_id>', methods=['POST'])
@jwt_required()
@admin_required
def approve_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    user.is_approved = True
    db.session.commit()
    # Here you would typically send an email to the user informing them of the approval
    return jsonify({"msg": "User approved successfully"}), 200

@app.route('/api/admin/reject_user/<int:user_id>', methods=['POST'])
@jwt_required()
@admin_required
def reject_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    if user.role == 'student':
        student = Student.query.filter_by(user_id=user.id).first()
        if student:
            db.session.delete(student)
    elif user.role == 'lecturer':
        lecturer = Lecturer.query.filter_by(user_id=user.id).first()
        if lecturer:
            db.session.delete(lecturer)
    elif user.role == 'admin':
        admin = Admin.query.filter_by(user_id=user.id).first()
        if admin:
            db.session.delete(admin)
    
    db.session.delete(user)
    db.session.commit()
    
    # Here you would typically send an email to the user informing them of the rejection
    return jsonify({"msg": "User rejected and removed from the system"}), 200

@app.route('/api/lecturer/timetable', methods=['GET'])
@jwt_required()
def get_lecturer_timetable():
    lecturer_id = get_jwt_identity()
    lecturer = User.query.get(lecturer_id)
    if not lecturer or lecturer.role != 'lecturer':
        return jsonify({"error": "Unauthorized"}), 403

    # Get all courses the lecturer is teaching
    courses = Course.query.join(CourseUnit).join(Timetable).filter(Timetable.lecturer_id == lecturer_id).distinct().all()

    courses_data = []
    for course in courses:
        course_units = CourseUnit.query.filter_by(course_id=course.id).all()
        timetable_entries = []
        for unit in course_units:
            entries = Timetable.query.filter_by(course_unit_id=unit.id, lecturer_id=lecturer_id).all()
            for entry in entries:
                timetable_entries.append({
                    "id": entry.id,
                    "day": entry.day.value,
                    "startTime": entry.start_time.strftime('%H:%M'),
                    "endTime": entry.end_time.strftime('%H:%M'),
                    "room": entry.room,
                    "courseUnit": {
                        "id": unit.id,
                        "code": unit.code,
                        "name": unit.name
                    }
                })
        
        courses_data.append({
            "id": course.id,
            "name": course.name,
            "timetableEntries": timetable_entries
        })

    return jsonify(courses_data), 200
  
@app.route('/api/student/timetable', methods=['GET'])
@jwt_required()
def get_student_timetable():
    student_id = get_jwt_identity()
    student = User.query.get(student_id)
    if not student or student.role != 'student':
        return jsonify({"error": "Unauthorized"}), 403

    # Assuming students are associated with a course
    # You might need to adjust this based on your actual data model
    course = student.course

    if not course:
        return jsonify({"error": "No course associated with this student"}), 404

    timetable_entries = []
    for unit in course.course_units:
        entries = Timetable.query.filter_by(course_unit_id=unit.id).all()
        for entry in entries:
            timetable_entries.append({
                "id": entry.id,
                "day": entry.day.value,
                "startTime": entry.start_time.strftime('%H:%M'),
                "endTime": entry.end_time.strftime('%H:%M'),
                "room": entry.room,
                "courseUnit": {
                    "id": unit.id,
                    "code": unit.code,
                    "name": unit.name
                },
                "lecturer": entry.lecturer.name
            })

    course_data = {
        "id": course.id,
        "name": course.name,
        "timetableEntries": timetable_entries
    }

    return jsonify([course_data]), 200

@app.route('/api/academic-years', methods=['GET'])
def get_academic_years():
    years = AcademicYear.query.all()
    return jsonify([{'id': year.id, 'year': year.year} for year in years])

@app.route('/api/semesters', methods=['GET'])
def get_semesters():
    semesters = Semester.query.all()
    return jsonify([{'id': semester.id, 'name': semester.name, 'academicYear': semester.academic_year.year} for semester in semesters])

@app.route('/api/colleges', methods=['GET'])
def get_colleges():
    colleges = College.query.all()
    return jsonify([{'id': college.id, 'name': college.name} for college in colleges])

@app.route('/api/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return jsonify([{'id': course.id, 'code': course.code, 'name': course.name, 'college': course.college.name} for course in courses])

@app.route('/api/student/dashboard', methods=['GET'])
@jwt_required()
def get_student_dashboard():
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()
    
    if not student:
        return jsonify({"error": "Student not found"}), 404

    # Get timetable
    timetable = Timetable.query.join(CourseUnit).filter(
        CourseUnit.course_id == student.course_id,
        Timetable.semester_id == student.semester_id
    ).order_by(Timetable.day, Timetable.start_time).all()

    # Get attendance stats
    total_classes = Attendance.query.filter_by(student_id=user_id).count()
    classes_attended = Attendance.query.filter(
        and_(
            Attendance.student_id == user_id,
            Attendance.check_out_time.isnot(None)
        )
    ).count()
    attendance_percentage = (classes_attended / total_classes * 100) if total_classes > 0 else 0

    # Get upcoming classes
    now = datetime.now()
    upcoming_classes = Timetable.query.join(CourseUnit).filter(
        CourseUnit.course_id == student.course_id,
        Timetable.semester_id == student.semester_id,
        Timetable.day >= DayOfWeek(now.strftime('%A')),
        Timetable.start_time > now.time()
    ).order_by(Timetable.day, Timetable.start_time).limit(5).all()

    def get_lecturer_name(lecturer_id):
        lecturer = Lecturer.query.filter_by(user_id=lecturer_id).first()
        return lecturer.name if lecturer else "Unknown"

    dashboard_data = {
        "student_name": student.name,
        "timetable": [
            {
                "day": entry.day.value,
                "start_time": entry.start_time.strftime('%H:%M'),
                "end_time": entry.end_time.strftime('%H:%M'),
                "course_name": entry.course_unit.name,
                "lecturer_name": get_lecturer_name(entry.lecturer_id)
            } for entry in timetable
        ],
        "attendance_stats": {
            "total_classes": total_classes,
            "classes_attended": classes_attended,
            "attendance_percentage": attendance_percentage
        },
        "upcoming_classes": [
            {
                "day": entry.day.value,
                "start_time": entry.start_time.strftime('%H:%M'),
                "end_time": entry.end_time.strftime('%H:%M'),
                "course_name": entry.course_unit.name,
                "lecturer_name": get_lecturer_name(entry.lecturer_id)
            } for entry in upcoming_classes
        ]
    }

    return jsonify(dashboard_data), 200

@app.route('/api/lecturer/dashboard', methods=['GET'])
@jwt_required()
def get_lecturer_dashboard():
    user_id = get_jwt_identity()
    lecturer = Lecturer.query.filter_by(user_id=user_id).first()
    
    if not lecturer:
        return jsonify({"error": "Lecturer not found"}), 404

    # Get timetable
    timetable = Timetable.query.join(CourseUnit).filter(
        Timetable.lecturer_id == user_id
    ).order_by(Timetable.day, Timetable.start_time).all()

    # Get upcoming classes
    now = datetime.now()
    upcoming_classes = Timetable.query.join(CourseUnit).filter(
        Timetable.lecturer_id == user_id,
        Timetable.day >= DayOfWeek(now.strftime('%A')),
        Timetable.start_time > now.time()
    ).order_by(Timetable.day, Timetable.start_time).limit(5).all()

    # Get course statistics
    course_stats = []
    for entry in timetable:
        total_students = Student.query.filter_by(course_id=entry.course_unit.course_id).count()
        total_attendances = Attendance.query.filter_by(timetable_id=entry.id).count()
        attendance_rate = (total_attendances / total_students * 100) if total_students > 0 else 0
        
        course_stats.append({
            "course_name": entry.course_unit.name,
            "total_students": total_students,
            "total_attendances": total_attendances,
            "attendance_rate": attendance_rate
        })

    dashboard_data = {
        "lecturer_name": lecturer.name,
        "timetable": [
            {
                "day": entry.day.value,
                "start_time": entry.start_time.strftime('%H:%M'),
                "end_time": entry.end_time.strftime('%H:%M'),
                "course_name": entry.course_unit.name,
                "room": entry.room
            } for entry in timetable
        ],
        "upcoming_classes": [
            {
                "day": entry.day.value,
                "start_time": entry.start_time.strftime('%H:%M'),
                "end_time": entry.end_time.strftime('%H:%M'),
                "course_name": entry.course_unit.name,
                "room": entry.room
            } for entry in upcoming_classes
        ],
        "course_stats": course_stats
    }

    return jsonify(dashboard_data), 200
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, and_

@app.route('/api/admin/dashboard', methods=['GET'])
@jwt_required()
def get_admin_dashboard():
    user_id = get_jwt_identity()
    admin = Admin.query.filter_by(user_id=user_id).first()
    
    if not admin:
        return jsonify({"error": "Admin not found"}), 404

    # Get overall statistics
    total_students = Student.query.count()
    total_lecturers = Lecturer.query.count()
    total_courses = Course.query.count()
    total_attendances = Attendance.query.count()

    # Get recent registrations
    recent_registrations = User.query.order_by(User.id.desc()).limit(5).all()

    # Get courses with highest attendance rates
    course_attendance = db.session.query(
        Course.name,
        func.count(Attendance.id).label('attendance_count'),
        func.count(Student.id).label('student_count')
    ).join(CourseUnit, Course.id == CourseUnit.course_id)\
     .join(Timetable, CourseUnit.id == Timetable.course_unit_id)\
     .join(Attendance, Timetable.id == Attendance.timetable_id)\
     .join(Student, Course.id == Student.course_id)\
     .group_by(Course.id)\
     .order_by((func.count(Attendance.id) / func.count(Student.id)).desc())\
     .limit(5).all()

    top_courses = [
        {
            "name": course.name,
            "attendance_rate": (course.attendance_count / course.student_count * 100) if course.student_count > 0 else 0
        } for course in course_attendance
    ]

    # Get lecturers with most classes
    top_lecturers = db.session.query(
        Lecturer.name,
        func.count(Timetable.id).label('class_count')
    ).join(User, Lecturer.user_id == User.id)\
     .join(Timetable, User.id == Timetable.lecturer_id)\
     .group_by(Lecturer.id)\
     .order_by(func.count(Timetable.id).desc())\
     .limit(5).all()

    def get_user_name(user):
        if user.role == 'student':
            student = Student.query.filter_by(user_id=user.id).first()
            return student.name if student else "Unknown"
        elif user.role == 'lecturer':
            lecturer = Lecturer.query.filter_by(user_id=user.id).first()
            return lecturer.name if lecturer else "Unknown"
        else:
            return "Unknown"

    dashboard_data = {
        "admin_name": admin.name,
        "overall_stats": {
            "total_students": total_students,
            "total_lecturers": total_lecturers,
            "total_courses": total_courses,
            "total_attendances": total_attendances
        },
        "recent_registrations": [
            {
                "name": get_user_name(user),
                "role": user.role,
                "email": user.email,
                "date": user.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(user, 'created_at') else "Unknown"
            } for user in recent_registrations
        ],
        "top_courses": top_courses,
        "top_lecturers": [
            {
                "name": lecturer.name,
                "class_count": lecturer.class_count
            } for lecturer in top_lecturers
        ]
    }

    return jsonify(dashboard_data), 200

@app.route('/api/check-attendance', methods=['POST'])
def check_attendance():
    image_data = request.json.get('image')
    
    if not image_data:
        logger.error("No image data received")
        return jsonify({"error": "No image data received"}), 400
    
    try:
        # Remove the data URL prefix if present
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        
        # Open image using PIL
        img = Image.open(BytesIO(image_bytes))
        
        # Convert PIL Image to numpy array for OpenCV
        img_np = np.array(img)
        
        # Convert RGB to BGR (OpenCV uses BGR)
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        
        logger.info(f"Image processed successfully. Shape: {img_np.shape}")
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return jsonify({"error": "Failed to process image"}), 400
    
    # Perform face detection and recognition
    face_recognition = FaceRecognition.get_instance()
    faces = face_recognition.detect_faces(img_np)
    
    if not faces:
        logger.info("No face detected in the image")
        return jsonify({"message": "No face detected"}), 200
    
    if len(faces) > 1:
        logger.warning("Multiple faces detected in the image")
        return jsonify({"warning": "Multiple faces detected. Please ensure only one person is in the frame."}), 200
    
    face = faces[0]
    aligned_face = face_recognition.align_face(img_np, face)
    
    # Check face quality
    if not face_recognition.check_face_quality(aligned_face):
        return jsonify({"message": "Poor quality image. Please try again with better lighting and less blur."}), 200
    
    face_embedding = face_recognition.get_face_embedding(aligned_face)
    
    if face_embedding is None:
        return jsonify({"error": "Failed to generate face embedding"}), 500
    
    # Find matching student
    all_students = Student.query.all()
    
    matching_student = None
    best_match_distance = float('inf')
    for student in all_students:
        # Skip the first student 
        if student.id == 1:
            continue
        if student.face_encoding:
            try:
                stored_embeddings = [np.array(emb) for emb in student.face_encoding]
                is_match, distance = face_recognition.recognize_face(face_embedding, stored_embeddings)
                logger.info(f"Student {student.id}: match={is_match}, distance={distance}")
                if is_match and distance < best_match_distance:
                    best_match_distance = distance
                    matching_student = student
            except Exception as e:
                logger.error(f"Error comparing faces for student {student.id}: {str(e)}")
                continue
    
    if matching_student is None:
        return jsonify({"message": "Face not recognized as a registered student"}), 200

    now = datetime.now()
    
    # Check for active sessions
    active_session = Attendance.query.filter_by(student_id=matching_student.user_id, check_out_time=None).first()
    
    # Find the next scheduled class
    next_class = Timetable.query.join(CourseUnit).filter(
        CourseUnit.course_id == matching_student.course_id,
        Timetable.semester_id == matching_student.semester_id,
        ((Timetable.day > DayOfWeek(now.strftime('%A'))) |
         ((Timetable.day == DayOfWeek(now.strftime('%A'))) & (Timetable.start_time > now.time())))
    ).order_by(Timetable.day, Timetable.start_time).first()

    # Get all classes for the week
    all_classes = Timetable.query.join(CourseUnit).filter(
        CourseUnit.course_id == matching_student.course_id,
        Timetable.semester_id == matching_student.semester_id
    ).order_by(Timetable.day, Timetable.start_time).all()

    response_data = {
        "student_name": matching_student.name,
        "current_time": now.strftime('%Y-%m-%d %H:%M:%S'),
        "active_session": None,
        "next_lecture": None,
        "weekly_schedule": []
    }

    if active_session:
        timetable_entry = active_session.timetable
        response_data["active_session"] = {
            "course": timetable_entry.course_unit.name,
            "start_time": timetable_entry.start_time.strftime('%H:%M'),
            "end_time": timetable_entry.end_time.strftime('%H:%M'),
            "room": timetable_entry.room
        }
        if now >= timetable_entry.end_time - timedelta(minutes=30):
            active_session.check_out_time = now
            db.session.commit()
            response_data["message"] = "Session ended successfully"
        else:
            response_data["message"] = "Active session ongoing"
    elif next_class:
        # Convert the day value to an integer
        day_mapping = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }
        next_class_day = day_mapping.get(next_class.day.value, 0)  # Default to Monday (0) if not found
        
        next_class_datetime = datetime.combine(
            now.date() + timedelta(days=(next_class_day - now.weekday() + 7) % 7),
            next_class.start_time
        )
        time_until_next = next_class_datetime - now
        response_data["next_lecture"] = {
            "course": next_class.course_unit.name,
            "day": next_class.day.value,
            "date": next_class_datetime.strftime('%Y-%m-%d'),
            "start_time": next_class.start_time.strftime('%H:%M'),
            "end_time": next_class.end_time.strftime('%H:%M'),
            "room": next_class.room,
            "time_until": str(time_until_next).split('.')[0]
        }
        if time_until_next <= timedelta(minutes=30):
            response_data["message"] = f"Next class starts in {str(time_until_next).split('.')[0]}"
        else:
            response_data["message"] = "No immediate upcoming classes"
    else:
        response_data["message"] = "No upcoming classes scheduled"
    for class_ in all_classes:
        response_data["weekly_schedule"].append({
            "day": class_.day.value,
            "course": class_.course_unit.name,
            "start_time": class_.start_time.strftime('%H:%M'),
            "end_time": class_.end_time.strftime('%H:%M'),
            "room": class_.room
        })

    return jsonify(response_data), 200


# Admin Reporting Features
def get_admin_reports():
    return {
        "overall_attendance_rate": get_overall_attendance_rate(),
        "attendance_by_college": get_attendance_by_college(),
        "attendance_trends": get_attendance_trends(),
        "top_attending_courses": get_top_attending_courses(),
        "low_attending_courses": get_low_attending_courses(),
        "lecturer_performance": get_lecturer_performance(),
        "student_engagement": get_student_engagement(),
    }

def get_overall_attendance_rate():
    total_sessions = db.session.query(func.count(Attendance.id)).scalar()
    attended_sessions = db.session.query(func.count(Attendance.id)).filter(Attendance.check_out_time.isnot(None)).scalar()
    return (attended_sessions / total_sessions) * 100 if total_sessions > 0 else 0

def get_attendance_by_college():
    return db.session.query(
        College.name,
        func.avg(case([(Attendance.check_out_time.isnot(None), 100)], else_=0)).label('attendance_rate')
    ).join(Course, College.id == Course.college_id)\
     .join(CourseUnit, Course.id == CourseUnit.course_id)\
     .join(Timetable, CourseUnit.id == Timetable.course_unit_id)\
     .join(Attendance, Timetable.id == Attendance.timetable_id)\
     .group_by(College.name).all()

def get_attendance_trends():
    thirty_days_ago = datetime.now() - timedelta(days=30)
    return db.session.query(
        func.date(Attendance.date).label('date'),
        func.count(Attendance.id).label('total_sessions'),
        func.sum(case([(Attendance.check_out_time.isnot(None), 1)], else_=0)).label('attended_sessions')
    ).filter(Attendance.date >= thirty_days_ago)\
     .group_by(func.date(Attendance.date))\
     .order_by(func.date(Attendance.date)).all()

def get_top_attending_courses(limit=5):
    return db.session.query(
        Course.name,
        func.avg(case([(Attendance.check_out_time.isnot(None), 100)], else_=0)).label('attendance_rate')
    ).join(CourseUnit, Course.id == CourseUnit.course_id)\
     .join(Timetable, CourseUnit.id == Timetable.course_unit_id)\
     .join(Attendance, Timetable.id == Attendance.timetable_id)\
     .group_by(Course.name)\
     .order_by(func.avg(case([(Attendance.check_out_time.isnot(None), 100)], else_=0)).desc())\
     .limit(limit).all()

def get_low_attending_courses(limit=5):
    return db.session.query(
        Course.name,
        func.avg(case([(Attendance.check_out_time.isnot(None), 100)], else_=0)).label('attendance_rate')
    ).join(CourseUnit, Course.id == CourseUnit.course_id)\
     .join(Timetable, CourseUnit.id == Timetable.course_unit_id)\
     .join(Attendance, Timetable.id == Attendance.timetable_id)\
     .group_by(Course.name)\
     .order_by(func.avg(case([(Attendance.check_out_time.isnot(None), 100)], else_=0)).asc())\
     .limit(limit).all()

def get_lecturer_performance():
    return db.session.query(
        User.name.label('lecturer_name'),
        func.count(Timetable.id).label('total_sessions'),
        func.avg(case([(Attendance.check_out_time.isnot(None), 100)], else_=0)).label('average_attendance_rate')
    ).join(Timetable, User.id == Timetable.lecturer_id)\
     .join(Attendance, Timetable.id == Attendance.timetable_id)\
     .filter(User.role == 'lecturer')\
     .group_by(User.id)\
     .order_by(func.avg(case([(Attendance.check_out_time.isnot(None), 100)], else_=0)).desc()).all()

def get_student_engagement():
    return db.session.query(
        User.name.label('student_name'),
        func.count(Attendance.id).label('total_sessions'),
        func.sum(case([(Attendance.check_out_time.isnot(None), 1)], else_=0)).label('attended_sessions'),
        (func.sum(case([(Attendance.check_out_time.isnot(None), 1)], else_=0)) / func.count(Attendance.id) * 100).label('attendance_rate')
    ).join(Attendance, User.id == Attendance.student_id)\
     .filter(User.role == 'student')\
     .group_by(User.id)\
     .order_by((func.sum(case([(Attendance.check_out_time.isnot(None), 1)], else_=0)) / func.count(Attendance.id) * 100).desc()).all()

# Student Reporting Features
def get_student_reports(student_id):
    return {
        "personal_attendance_rate": get_personal_attendance_rate(student_id),
        "attendance_by_course": get_attendance_by_course(student_id),
        "attendance_trend": get_student_attendance_trend(student_id),
        "missed_classes": get_missed_classes(student_id),
        "upcoming_classes": get_upcoming_classes(student_id),
    }

def get_personal_attendance_rate(student_id):
    total_sessions = db.session.query(func.count(Attendance.id)).filter(Attendance.student_id == student_id).scalar()
    attended_sessions = db.session.query(func.count(Attendance.id)).filter(and_(Attendance.student_id == student_id, Attendance.check_out_time.isnot(None))).scalar()
    return (attended_sessions / total_sessions) * 100 if total_sessions > 0 else 0

def get_attendance_by_course(student_id):
    return db.session.query(
        Course.name,
        func.count(Attendance.id).label('total_sessions'),
        func.sum(case([(Attendance.check_out_time.isnot(None), 1)], else_=0)).label('attended_sessions'),
        (func.sum(case([(Attendance.check_out_time.isnot(None), 1)], else_=0)) / func.count(Attendance.id) * 100).label('attendance_rate')
    ).join(CourseUnit, Course.id == CourseUnit.course_id)\
     .join(Timetable, CourseUnit.id == Timetable.course_unit_id)\
     .join(Attendance, Timetable.id == Attendance.timetable_id)\
     .filter(Attendance.student_id == student_id)\
     .group_by(Course.id).all()

def get_student_attendance_trend(student_id):
    thirty_days_ago = datetime.now() - timedelta(days=30)
    return db.session.query(
        func.date(Attendance.date).label('date'),
        func.count(Attendance.id).label('total_sessions'),
        func.sum(case([(Attendance.check_out_time.isnot(None), 1)], else_=0)).label('attended_sessions')
    ).filter(and_(Attendance.student_id == student_id, Attendance.date >= thirty_days_ago))\
     .group_by(func.date(Attendance.date))\
     .order_by(func.date(Attendance.date)).all()

def get_missed_classes(student_id):
    return db.session.query(
        Course.name,
        Timetable.day,
        Timetable.start_time,
        Timetable.end_time,
        Attendance.date
    ).join(CourseUnit, Course.id == CourseUnit.course_id)\
     .join(Timetable, CourseUnit.id == Timetable.course_unit_id)\
     .join(Attendance, Timetable.id == Attendance.timetable_id)\
     .filter(and_(Attendance.student_id == student_id, Attendance.check_out_time.is_(None)))\
     .order_by(Attendance.date.desc()).limit(10).all()

def get_upcoming_classes(student_id):
    today = datetime.now().date()
    student = Student.query.filter_by(user_id=student_id).first()
    return db.session.query(
        Course.name,
        Timetable.day,
        Timetable.start_time,
        Timetable.end_time,
        Timetable.room
    ).join(CourseUnit, Course.id == CourseUnit.course_id)\
     .join(Timetable, CourseUnit.id == Timetable.course_unit_id)\
     .filter(Course.id == student.course_id)\
     .filter(or_(
         and_(Timetable.day == today.strftime('%A'), Timetable.start_time > datetime.now().time()),
         Timetable.day > today.strftime('%A')
     ))\
     .order_by(case(
         {day: index for index, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])}
     ))\
     .order_by(Timetable.start_time).limit(5).all()

# Lecturer Reporting Features
def get_lecturer_reports(lecturer_id):
    return {
        "course_attendance_rates": get_course_attendance_rates(lecturer_id),
        "recent_class_attendance": get_recent_class_attendance(lecturer_id),
        "student_performance": get_student_performance(lecturer_id),
        "attendance_trends_by_course": get_attendance_trends_by_course(lecturer_id),
        "upcoming_classes": get_lecturer_upcoming_classes(lecturer_id),
    }

def get_course_attendance_rates(lecturer_id):
    return db.session.query(
        Course.name,
        func.count(Attendance.id).label('total_sessions'),
        func.sum(case([(Attendance.check_out_time.isnot(None), 1)], else_=0)).label('attended_sessions'),
        (func.sum(case([(Attendance.check_out_time.isnot(None), 1)], else_=0)) / func.count(Attendance.id) * 100).label('attendance_rate')
    ).join(CourseUnit, Course.id == CourseUnit.course_id)\
     .join(Timetable, CourseUnit.id == Timetable.course_unit_id)\
     .join(Attendance, Timetable.id == Attendance.timetable_id)\
     .filter(Timetable.lecturer_id == lecturer_id)\
     .group_by(Course.id).all()

def get_recent_class_attendance(lecturer_id):
    return db.session.query(
        Course.name,
        Timetable.day,
        Timetable.start_time,
        Timetable.end_time,
        func.count(Attendance.id).label('total_students'),
        func.sum(case([(Attendance.check_out_time.isnot(None), 1)], else_=0)).label('attended_students')
    ).join(CourseUnit, Course.id == CourseUnit.course_id)\
     .join(Timetable, CourseUnit.id == Timetable.course_unit_id)\
     .join(Attendance, Timetable.id == Attendance.timetable_id)\
     .filter(Timetable.lecturer_id == lecturer_id)\
     .group_by(Timetable.id)\
     .order_by(Attendance.date.desc(), Timetable.start_time.desc())\
     .limit(5).all()

def get_student_performance(lecturer_id):
    return db.session.query(
        User.name.label('student_name'),
        Course.name.label('course_name'),
        func.count(Attendance.id).label('total_sessions'),
        func.sum(case([(Attendance.check_out_time.isnot(None), 1)], else_=0)).label('attended_sessions'),
        (func.sum(case([(Attendance.check_out_time.isnot(None), 1)], else_=0)) / func.count(Attendance.id) * 100).label('attendance_rate')
    ).join(Attendance, User.id == Attendance.student_id)\
     .join(Timetable, Attendance.timetable_id == Timetable.id)\
     .join(CourseUnit, Timetable.course_unit_id == CourseUnit.id)\
     .join(Course, CourseUnit.course_id == Course.id)\
     .filter(Timetable.lecturer_id == lecturer_id)\
     .group_by(User.id, Course.id)\
     .order_by(Course.name, (func.sum(case([(Attendance.check_out_time.isnot(None), 1)], else_=0)) / func.count(Attendance.id) * 100).desc()).all()

def get_attendance_trends_by_course(lecturer_id):
    thirty_days_ago = datetime.now() - timedelta(days=30)
    return db.session.query(
        Course.name,
        func.date(Attendance.date).label('date'),
        func.count(Attendance.id).label('total_sessions'),
        func.sum(case([(Attendance.check_out_time.isnot(None), 1)], else_=0)).label('attended_sessions')
    ).join(CourseUnit, Course.id == CourseUnit.course_id)\
     .join(Timetable, CourseUnit.id == Timetable.course_unit_id)\
     .join(Attendance, Timetable.id == Attendance.timetable_id)\
     .filter(and_(Timetable.lecturer_id == lecturer_id, Attendance.date >= thirty_days_ago))\
     .group_by(Course.id, func.date(Attendance.date))\
     .order_by(Course.name, func.date(Attendance.date)).all()

def get_lecturer_upcoming_classes(lecturer_id):
    today = datetime.now().date()
    return db.session.query(
        Course.name,
        Timetable.day,
        Timetable.start_time,
        Timetable.end_time,
        Timetable.room
    ).join(CourseUnit, Course.id == CourseUnit.course_id)\
     .join(Timetable, CourseUnit.id == Timetable.course_unit_id)\
     .filter(Timetable.lecturer_id == lecturer_id)\
     .filter(or_(
         and_(Timetable.day == today.strftime('%A'), Timetable.start_time > datetime.now().time()),
         Timetable.day > today.strftime('%A')
     ))\
     .order_by(case(
         {day: index for index, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])}
     ))\
     .order_by(Timetable.start_time).limit(5).all()

# New API endpoints for reports

@app.route('/api/admin/reports', methods=['GET'])
@jwt_required()
@admin_required
def admin_reports():
    try:
        reports = get_admin_reports()
        return jsonify(reports), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/student/reports', methods=['GET'])
@jwt_required()
def student_reports():
    try:
        student_id = get_jwt_identity()
        reports = get_student_reports(student_id)
        return jsonify(reports), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lecturer/reports', methods=['GET'])
@jwt_required()
def lecturer_reports():
    try:
        lecturer_id = get_jwt_identity()
        reports = get_lecturer_reports(lecturer_id)
        return jsonify(reports), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Utility function for pagination
def paginate(query, page, per_page):
    items = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': [item._asdict() for item in items.items],
        'total': items.total,
        'pages': items.pages,
        'page': page
    }

# Example of a paginated endpoint
@app.route('/api/admin/student-engagement', methods=['GET'])
@jwt_required()
@admin_required
def admin_student_engagement():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = db.session.query(
            User.name.label('student_name'),
            func.count(Attendance.id).label('total_sessions'),
            func.sum(case([(Attendance.check_out_time.isnot(None), 1)], else_=0)).label('attended_sessions'),
            (func.sum(case([(Attendance.check_out_time.isnot(None), 1)], else_=0)) / func.count(Attendance.id) * 100).label('attendance_rate')
        ).join(Attendance, User.id == Attendance.student_id)\
         .filter(User.role == 'student')\
         .group_by(User.id)\
         .order_by((func.sum(case([(Attendance.check_out_time.isnot(None), 1)], else_=0)) / func.count(Attendance.id) * 100).desc())
        
        return jsonify(paginate(query, page, per_page)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add more specific endpoints as needed, for example:
@app.route('/api/lecturer/course-attendance/<int:course_id>', methods=['GET'])
@jwt_required()
def lecturer_course_attendance(course_id):
    try:
        lecturer_id = get_jwt_identity()
        attendance_data = db.session.query(
            Attendance.date,
            func.count(Attendance.id).label('total_students'),
            func.sum(case([(Attendance.check_out_time.isnot(None), 1)], else_=0)).label('attended_students')
        ).join(Timetable, Attendance.timetable_id == Timetable.id)\
         .join(CourseUnit, Timetable.course_unit_id == CourseUnit.id)\
         .filter(and_(Timetable.lecturer_id == lecturer_id, CourseUnit.course_id == course_id))\
         .group_by(Attendance.date)\
         .order_by(Attendance.date.desc())\
         .limit(30).all()
        
        return jsonify([{
            'date': data.date.strftime('%Y-%m-%d'),
            'total_students': data.total_students,
            'attended_students': data.attended_students,
            'attendance_rate': (data.attended_students / data.total_students * 100) if data.total_students > 0 else 0
        } for data in attendance_data]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Example of how to handle date range filters
@app.route('/api/admin/attendance-trends', methods=['GET'])
@jwt_required()
@admin_required
def admin_attendance_trends():
    try:
        start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        trends = db.session.query(
            func.date(Attendance.date).label('date'),
            func.count(Attendance.id).label('total_sessions'),
            func.sum(case([(Attendance.check_out_time.isnot(None), 1)], else_=0)).label('attended_sessions')
        ).filter(and_(Attendance.date >= start_date, Attendance.date <= end_date))\
         .group_by(func.date(Attendance.date))\
         .order_by(func.date(Attendance.date)).all()
        
        return jsonify([{
            'date': trend.date.strftime('%Y-%m-%d'),
            'total_sessions': trend.total_sessions,
            'attended_sessions': trend.attended_sessions,
            'attendance_rate': (trend.attended_sessions / trend.total_sessions * 100) if trend.total_sessions > 0 else 0
        } for trend in trends]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # augment_existing_data(
        #     num_new_students=200,
        #     num_new_lecturers=15,
        #     num_new_courses=8,
        #     start_date=datetime(2024, 9, 1),
        #     end_date=datetime(2024, 12, 31)
        # )
    app.run(debug=True)