from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_reuploaded import configure_uploads, UploadSet, IMAGES
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from functools import wraps
from sqlalchemy import Enum
import enum
from datetime import datetime, time  # Add this import
from sqlalchemy.exc import IntegrityError
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# from claude_facial_recognition import FaceRecognition
from claude_face_recognition import FaceRecognition

app = Flask(__name__)
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization"]}})

# Configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'  # Use your preferred database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://laravel_user:laravel_user@localhost/attendance_system_v1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Initialize FaceRecognition
face_recognition = FaceRecognition.get_instance()

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student', 'lecturer', 'admin'
    is_approved = db.Column(db.Boolean, default=False)
  
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
    year = db.Column(db.Integer, nullable=False)
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

# Routes
@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        # Preflight request. Reply successfully:
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    logger.debug(f"Raw data: {request.get_data()}")
    logger.debug(f"Form data: {request.form}")
    logger.debug(f"Files: {request.files}")

    data = request.form.to_dict()
    files = request.files

    required_fields = ['email', 'password', 'name', 'role', 'student_id', 'academic_year_id', 'course_id', 'college_id', 'semester_id']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({"msg": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"msg": "Email already registered"}), 400

    try:
        user = User(email=data['email'], role=data['role'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()

        if data['role'] == 'student':
            student = Student(
                user_id=user.id,
                student_id=data['student_id'],
                name=data['name'],
                academic_year_id=int(data['academic_year_id']),
                course_id=int(data['course_id']),
                college_id=int(data['college_id']),
                semester_id=int(data['semester_id'])
            )
            
            face_images = [files[key] for key in files.keys() if key.startswith('faceImage')]
            if not face_images:
                return jsonify({"msg": "At least one facial image is required"}), 400
            
            face_encodings = []
            for image in face_images:
                image_data = face_recognition.load_image_file(image)
                encoding = face_recognition.face_encodings(image_data)
                if not encoding:
                    return jsonify({"msg": "Failed to process facial image"}), 400
                face_encodings.append(encoding[0].tolist())
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

        db.session.commit()
        return jsonify({"msg": "User registered successfully. Awaiting approval."}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during registration: {str(e)}")
        return jsonify({"msg": f"Error registering user: {str(e)}"}), 500

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

@app.route('/api/admin/pending_registrations', methods=['GET'])
@jwt_required()
@admin_required
def get_pending_registrations():
    pending_users = User.query.filter_by(is_approved=False).all()
    pending_data = []
    for user in pending_users:
        user_data = {"id": user.id, "email": user.email, "role": user.role}
        if user.role == 'student':
            student = Student.query.filter_by(user_id=user.id).first()
            if student:
                user_data.update({
                    "student_id": student.student_id,
                    "name": student.name,
                    "year": student.year,
                    "academic_year": student.academic_year,
                    "unit": student.unit,
                    "group": student.group,
                    "semester": student.semester
                })
        elif user.role == 'lecturer':
            lecturer = Lecturer.query.filter_by(user_id=user.id).first()
            if lecturer:
                user_data["name"] = lecturer.name
        pending_data.append(user_data)
    return jsonify(pending_data), 200

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
    
    # If rejecting a student, we need to delete the associated Student record
    if user.role == 'student':
        student = Student.query.filter_by(user_id=user.id).first()
        if student:
            db.session.delete(student)
    
    # If rejecting a lecturer, we need to delete the associated Lecturer record
    elif user.role == 'lecturer':
        lecturer = Lecturer.query.filter_by(user_id=user.id).first()
        if lecturer:
            db.session.delete(lecturer)
    
    # Delete the user
    db.session.delete(user)
    db.session.commit()
    
    # Here you would typically send an email to the user informing them of the rejection
    return jsonify({"msg": "User rejected and removed from the system"}), 200

@app.route('/api/admin/populate-sample-data', methods=['GET'])
def populate_sample_data():
    try:
        # Create Academic Year
        academic_year = AcademicYear(year="2023/2024")
        db.session.add(academic_year)

        # Create Semester
        semester = Semester(name="Semester I", academic_year=academic_year)
        db.session.add(semester)

        # Create College
        college = College(name="College of Computing and Information Sciences(CoCIS)")
        db.session.add(college)

        # Create Course
        course = Course(code="CS", name="Computer Science", college=college)  # Added code here
        db.session.add(course)

        # Create Course Units
        course_units = [
            CourseUnit(code="IST1104", name="Basic Mathematics", course=course),
            CourseUnit(code="IST1103", name="Introduction to ICT", course=course),
            CourseUnit(code="IST1102", name="Electronic Technology", course=course),
            CourseUnit(code="IST1100", name="Communication Skills", course=course),
            CourseUnit(code="IST1101", name="Discrete Structures", course=course)
        ]
        db.session.add_all(course_units)

        # Fetch existing lecturers
        lecturer1 = User.query.filter_by(email="thomas@gmail.com").first()
        # lecturer2 = User.query.filter_by(email="jane.smith@example.com").first()

        # if not lecturer1 or not lecturer2:
        #     return jsonify({"error": "Required lecturers not found. Please ensure they exist in the database."}), 400
        if not lecturer1 :
            return jsonify({"error": "Required lecturers not found. Please ensure they exist in the database."}), 400


        # Create Timetable entries
        timetable_entries = [
            Timetable(semester=semester, course_unit=course_units[0], day=DayOfWeek.THURSDAY, 
                      start_time=time(8, 0), end_time=time(10, 0), room="BCIT R004", lecturer=lecturer1),
            Timetable(semester=semester, course_unit=course_units[1], day=DayOfWeek.THURSDAY, 
                      start_time=time(10, 0), end_time=time(12, 0), room="BCIT R114", lecturer=lecturer1),
            Timetable(semester=semester, course_unit=course_units[2], day=DayOfWeek.THURSDAY, 
                      start_time=time(14, 0), end_time=time(16, 0), room="BCIT R204", lecturer=lecturer1),
            Timetable(semester=semester, course_unit=course_units[3], day=DayOfWeek.MONDAY,
                        start_time=time(8, 0), end_time=time(10, 0), room="BCIT R004", lecturer=lecturer1),
            Timetable(semester=semester, course_unit=course_units[4], day=DayOfWeek.TUESDAY,
                        start_time=time(8, 0), end_time=time(10, 0), room="BCIT R004", lecturer=lecturer1)
        ]
        db.session.add_all(timetable_entries)

        db.session.commit()
        return jsonify({"message": "Sample data populated successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

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

# api.get("/academic-years"),
#           api.get("/semesters"),
#           api.get("/colleges"),
#           api.get("/courses"),
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)