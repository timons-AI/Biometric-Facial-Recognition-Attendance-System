from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_migrate import Migrate
import datetime
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://laravel_user:laravel_user@localhost/demo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)
CORS(app)
migrate = Migrate(app, db)

# Define the models
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

# Define Schemas for serialization
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

# API Resources
class LecturerResource(Resource):
    def get(self):
        lecturers = Lecturer.query.all()
        return LecturerSchema(many=True).dump(lecturers)

class ClassResource(Resource):
    def get(self):
        classes = Class.query.all()
        return ClassSchema(many=True).dump(classes)

class TimetableResource(Resource):
    def get(self):
        timetable = Timetable.query.all()
        return TimetableSchema(many=True).dump(timetable)

class PopulateResource(Resource):
    def get(self):
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
        return {"message": "Database populated with sample data!"}, 201

# Add resources to API
api.add_resource(LecturerResource, '/api/lecturers')
api.add_resource(ClassResource, '/api/classes')
api.add_resource(TimetableResource, '/api/timetable')
api.add_resource(PopulateResource, '/populate')



if __name__ == '__main__':
    app.run(debug=True)