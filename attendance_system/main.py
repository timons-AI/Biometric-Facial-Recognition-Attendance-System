import cv2
import numpy as np
import time
import logging
from database import Database
from face_recognition import FaceRecognition
from datetime import datetime, timedelta
import pygame
import threading
import queue
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AttendanceSystem:
    def __init__(self):
        self.db = Database()
        self.face_recognition = FaceRecognition.get_instance()
        self.known_faces = self.load_known_faces()
        self.threshold = 0.6
        self.attendance_queue = queue.Queue()
        self.last_attendance_time = {}
        self.cooldown_period = timedelta(minutes=5)
        
        # Initialize Pygame for sound
        pygame.mixer.init()
        self.success_sound = "success.mp3"
        self.failure_sound = "failure.mp3"

        self.face_status = defaultdict(lambda: {"status": None, "time": 0})
        self.identification_duration = 10  # seconds
        self.sound_cooldown = 5  # seconds
        self.last_sound_time = 0

        self.face_detection_confidence = 0.5  # Adjust this value as needed
        self.min_face_size = 30  # Minimum face size in pixels
        self.max_face_size = 300  # Maximum face size in pixels
        self.face_trackers = {}
    
    def load_known_faces(self):
        try:
            query = "SELECT student_id, name, face_embedding FROM students"
            results = self.db.fetch_all(query)
            known_faces = {}
            for student_id, name, face_embedding_bytes in results:
                face_embedding = np.frombuffer(face_embedding_bytes, dtype=np.float32)
                known_faces[student_id] = {'name': name, 'embedding': face_embedding}
            return known_faces
        except Exception as e:
            logger.error(f"Error loading known faces: {e}")
            return {}
        
    def record_attendance(self, student_id):
        now = datetime.now()
        if student_id in self.last_attendance_time:
            if now - self.last_attendance_time[student_id] < self.cooldown_period:
                logger.info(f"Cooldown period for student {student_id} not yet expired")
                return False

        today = now.date()
        query = "SELECT * FROM attendance WHERE student_id = %s AND DATE(timestamp) = %s"
        params = (student_id, today)
        result = self.db.fetch_one(query, params)
       
        if not result:
            query = "INSERT INTO attendance (student_id, timestamp) VALUES (%s, NOW())"
            params = (student_id,)
            self.db.execute_query(query, params)
            self.last_attendance_time[student_id] = now
            logger.info(f"Attendance recorded for student {student_id}")
            return True
        else:
            logger.info(f"Attendance already recorded for student {student_id} today")
            return False

    def recognize_face(self, face_embedding):
        min_distance = float("inf")
        recognized_student_id = None
        recognized_name = None
        for student_id, data in self.known_faces.items():
            known_embedding = data['embedding']
            distance = np.linalg.norm(face_embedding - known_embedding)
            if distance < min_distance:
                min_distance = distance
                recognized_student_id = student_id
                recognized_name = data['name']
        if min_distance < self.threshold:
            return recognized_student_id, recognized_name
        return None, None

    def play_sound(self, sound_file):
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()

    def process_attendance_queue(self):
        while True:
            student_id, name = self.attendance_queue.get()
            if self.record_attendance(student_id):
                self.play_sound(self.success_sound)
            else:
                self.play_sound(self.failure_sound)
            self.attendance_queue.task_done()

    def run(self):
        cap = cv2.VideoCapture(0)
        
        # Start the attendance processing thread
        threading.Thread(target=self.process_attendance_queue, daemon=True).start()

        face_detection_interval = 5  # Detect faces every 5 frames
        frame_count = 0

        while True:
            try:
                ret, frame = cap.read()
                if not ret:
                    logger.error("Failed to capture frame")
                    break

                frame_count += 1
                current_time = time.time()

                # Update existing trackers
                self.update_trackers(frame)

                if frame_count % face_detection_interval == 0:
                    # Perform face detection
                    faces = self.face_recognition.detect_faces(frame, confidence_threshold=self.face_detection_confidence)
                    logger.debug(f"Detected {len(faces)} faces")
                    
                    for (x, y, w, h) in faces:
                        # Filter out faces that are too small or too large
                        if self.min_face_size <= w <= self.max_face_size and self.min_face_size <= h <= self.max_face_size:
                            face_image = frame[y:y+h, x:x+w]
                            face_embedding = self.face_recognition.get_face_embedding(face_image)
                            
                            if face_embedding is not None:
                                student_id, name = self.recognize_face(face_embedding)
                                face_key = f"{x},{y}"
                                
                                if student_id:
                                    logger.debug(f"Recognized student: {name} (ID: {student_id})")
                                    self.face_status[face_key] = {"status": "recognized", "time": current_time, "id": student_id, "name": name}
                                    try:
                                        self.face_trackers[face_key] = cv2.TrackerKCF_create()
                                        self.face_trackers[face_key].init(frame, (x, y, w, h))
                                    except Exception as e:
                                        logger.error(f"Error initializing tracker: {e}")
                                    
                                    if current_time - self.last_sound_time > self.sound_cooldown:
                                        self.attendance_queue.put((student_id, name))
                                        self.last_sound_time = current_time
                                else:
                                    logger.debug("Unknown face detected")
                                    self.face_status[face_key] = {"status": "unknown", "time": current_time}
                                    try:
                                        self.face_trackers[face_key] = cv2.TrackerKCF_create()
                                        self.face_trackers[face_key].init(frame, (x, y, w, h))
                                    except Exception as e:
                                        logger.error(f"Error initializing tracker: {e}")

                # Draw bounding boxes and labels
                self.draw_face_boxes(frame)

                # Add timestamp and total attendance
                self.add_frame_info(frame)

                cv2.imshow('Attendance System', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")

        cap.release()
        cv2.destroyAllWindows()
        self.db.close()
    
    def update_trackers(self, frame):
        for face_key, tracker in list(self.face_trackers.items()):
            try:
                success, bbox = tracker.update(frame)
                if success:
                    self.face_status[face_key]["time"] = time.time()
                else:
                    del self.face_trackers[face_key]
                    del self.face_status[face_key]
            except Exception as e:
                logger.error(f"Error updating tracker: {e}")
                del self.face_trackers[face_key]
                del self.face_status[face_key]

    def draw_face_boxes(self, frame):
        current_time = time.time()
        for face_key, status in list(self.face_status.items()):
            if current_time - status["time"] < self.identification_duration:
                x, y, w, h = map(int, self.face_trackers[face_key].get_position())
                if status["status"] == "recognized":
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, f"Name: {status['name']}, ID: {status['id']}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
                elif status["status"] == "unknown":
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)
            else:
                del self.face_status[face_key]
                if face_key in self.face_trackers:
                    del self.face_trackers[face_key]

    def add_frame_info(self, frame):
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, current_time_str, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        today = datetime.now().date()
        query = "SELECT COUNT(DISTINCT student_id) FROM attendance WHERE DATE(timestamp) = %s"
        params = (today,)
        count = self.db.fetch_one(query, params)[0]
        cv2.putText(frame, f"Total Attendance: {count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

if __name__ == "__main__":
    try:
        attendance_system = AttendanceSystem()
        attendance_system.run()
    except Exception as e:
        logger.error(f"An unexpected error occurred in the run method: {e}")