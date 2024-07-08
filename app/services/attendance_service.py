from app.models.attendance import Attendance
from app import db

def log_attendance(student_id):
    new_attendance = Attendance(student_id=student_id)
    db.session.add(new_attendance)
    db.session.commit()