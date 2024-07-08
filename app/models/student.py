from app import db
from datetime import datetime

# class Student(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     student_id = db.Column(db.String(20), unique=True, nullable=False)
#     face_images = db.Column(db.PickleType)  # Store multiple face image paths
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def __repr__(self):
#         return f'<Student {self.student_id}>'


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    face_images = db.relationship('FaceImage', backref='student', lazy=True)

class FaceImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)