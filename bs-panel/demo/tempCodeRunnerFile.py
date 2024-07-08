from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://laravel_user:laravel_user@localhost/demo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

# Create the tables
@app.before_first_request
def create_tables():
    db.create_all()

# Populate the database with sample data
@app.route('/populate')
def populate():
    # Sample data for lecturers extracted from the PDF
    lecturers = [
        Lecturer(first_name='Hawa', last_name='Nyende', email='hawa.nyende@example.com', password='hashed_password1'),
        Lecturer(first_name='Esther', last_name='Namirembe', email='esther.namirembe@example.com', password='hashed_password2'),
        Lecturer(first_name='Margaret', last_name='Nagwovuma', email='margaret.nagwovuma@example.com', password='hashed_password3'),
        Lecturer(first_name='Mercy', last_name='Amiyo', email='mercy.amiyo@example.com', password='hashed_password4'),
        Lecturer(first_name='Brian', last_name='Muchake', email='brian.muchake@example.com', password='hashed_password5')
    ]
    db.session.bulk_save_objects(lecturers)
    
    # Sample data for classes extracted from the PDF
    classes = [
        Class(class_name='IST 2102 Web Systems and Technologies I', lecturer_id=1),
        Class(class_name='IST 2104 Electronic Media Systems & Multimedia', lecturer_id=2),
        Class(class_name='BAM 2102 Entrepreneurship Principles', lecturer_id=3),
        Class(class_name='IST 2101 Data and Information Management II', lecturer_id=4),
        Class(class_name='IST 2103 Information System Security and Risk Management', lecturer_id=5)
    ]
    db.session.bulk_save_objects(classes)
    
    # Sample data for timetable extracted from the PDF
    timetable_entries = [
        # Monday
        Timetable(class_id=1, day_of_week='Monday', start_time=datetime.time(8, 0), end_time=datetime.time(9, 0)),
        Timetable(class_id=1, day_of_week='Monday', start_time=datetime.time(9, 0), end_time=datetime.time(10, 0)),
        Timetable(class_id=4, day_of_week='Monday', start_time=datetime.time(11, 0), end_time=datetime.time(12, 0)),
        Timetable(class_id=4, day_of_week='Monday', start_time=datetime.time(12, 0), end_time=datetime.time(13, 0)),
        Timetable(class_id=5, day_of_week='Monday', start_time=datetime.time(14, 0), end_time=datetime.time(15, 0)),
        Timetable(class_id=5, day_of_week='Monday', start_time=datetime.time(15, 0), end_time=datetime.time(16, 0)),
        
        # Tuesday
        Timetable(class_id=1, day_of_week='Tuesday', start_time=datetime.time(9, 0), end_time=datetime.time(10, 0)),
        Timetable(class_id=1, day_of_week='Tuesday', start_time=datetime.time(10, 0), end_time=datetime.time(11, 0)),
        Timetable(class_id=4, day_of_week='Tuesday', start_time=datetime.time(11, 0), end_time=datetime.time(12, 0)),
        Timetable(class_id=4, day_of_week='Tuesday', start_time=datetime.time(12, 0), end_time=datetime.time(13, 0)),
        Timetable(class_id=5, day_of_week='Tuesday', start_time=datetime.time(14, 0), end_time=datetime.time(15, 0)),
        Timetable(class_id=5, day_of_week='Tuesday', start_time=datetime.time(15, 0), end_time=datetime.time(16, 0)),
        
        # Wednesday
        Timetable(class_id=2, day_of_week='Wednesday', start_time=datetime.time(8, 0), end_time=datetime.time(9, 0)),
        Timetable(class_id=2, day_of_week='Wednesday', start_time=datetime.time(9, 0), end_time=datetime.time(10, 0)),
        Timetable(class_id=3, day_of_week='Wednesday', start_time=datetime.time(10, 0), end_time=datetime.time(11, 0)),
        Timetable(class_id=4, day_of_week='Wednesday', start_time=datetime.time(11, 0), end_time=datetime.time(12, 0)),
        Timetable(class_id=4, day_of_week='Wednesday', start_time=datetime.time(12, 0), end_time=datetime.time(13, 0)),
        Timetable(class_id=5, day_of_week='Wednesday', start_time=datetime.time(14, 0), end_time=datetime.time(15, 0)),
        Timetable(class_id=5, day_of_week='Wednesday', start_time=datetime.time(15, 0), end_time=datetime.time(16, 0)),
        
        # Thursday
        Timetable(class_id=2, day_of_week='Thursday', start_time=datetime.time(8, 0), end_time=datetime.time(9, 0)),
        Timetable(class_id=2, day_of_week='Thursday', start_time=datetime.time(9, 0), end_time=datetime.time(10, 0)),
        Timetable(class_id=3, day_of_week='Thursday', start_time=datetime.time(10, 0), end_time=datetime.time(11, 0)),
        Timetable(class_id=4, day_of_week='Thursday', start_time=datetime.time(11, 0), end_time=datetime.time(12, 0)),
        Timetable(class_id=4, day_of_week='Thursday', start_time=datetime.time(12, 0), end_time=datetime.time(13, 0)),
        Timetable(class_id=5, day_of_week='Thursday', start_time=datetime.time(14, 0), end_time=datetime.time(15, 0)),
        Timetable(class_id=5, day_of_week='Thursday', start_time=datetime.time(15, 0), end_time=datetime.time(16, 0)),
        
        # Friday
        Timetable(class_id=2, day_of_week='Friday', start_time=datetime.time(8, 0), end_time=datetime.time(9, 0)),
        Timetable(class_id=2, day_of_week='Friday', start_time=datetime.time(9, 0), end_time=datetime.time(10, 0)),
        Timetable(class_id=3, day_of_week='Friday', start_time=datetime.time(10, 0), end_time=datetime.time(11, 0)),
        Timetable(class_id=4, day_of_week='Friday', start_time=datetime.time(11, 0), end_time=datetime.time(12, 0)),
        Timetable(class_id=4, day_of_week='Friday', start_time=datetime.time(12, 0), end_time=datetime.time(13, 0)),
        Timetable(class_id=5, day_of_week='Friday', start_time=datetime.time(14, 0), end_time=datetime.time(15, 0)),
        Timetable(class_id=5, day_of_week='Friday', start_time=datetime.time(15, 0), end_time=datetime.time(16, 0))
    ]
    db.session.bulk_save_objects(timetable_entries)
    
    db.session.commit()
    return "Database populated with sample data!"

# Add to your Flask application

@app.route('/api/lecturers')
def get_lecturers():
    lecturers = Lecturer.query.all()
    return jsonify([{
        'lecturer_id': l.lecturer_id,
        'first_name': l.first_name,
        'last_name': l.last_name
    } for l in lecturers])

@app.route('/api/classes')
def get_classes():
    classes = Class.query.all()
    return jsonify([{
        'class_id': c.class_id,
        'class_name': c.class_name,
        'lecturer_id': c.lecturer_id
    } for c in classes])

@app.route('/api/timetable')
def get_timetable():
    timetable = Timetable.query.all()
    return jsonify([{
        'timetable_id': t.timetable_id,
        'class_id': t.class_id,
        'day_of_week': t.day_of_week,
        'start_time': t.start_time.strftime('%H:%M:%S'),
        'end_time': t.end_time.strftime('%H:%M:%S')
    } for t in timetable])


if __name__ == '__main__':
    app.run(debug=True)

