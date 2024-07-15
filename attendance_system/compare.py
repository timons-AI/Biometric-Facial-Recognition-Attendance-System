# app.py
from flask import Flask, render_template
from flask_socketio import SocketIO
import cv2
import base64
import numpy as np
from mtcnn import MTCNN
from deepface import DeepFace
from claude_face_recognition import FaceRecognition
from scipy.spatial.distance import cosine
import time

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize face recognition implementations
current_fr = FaceRecognition.get_instance()
detector = MTCNN()

registered_faces = {}

def register_face(name, image):
    faces = current_fr.detect_faces(image)
    if faces:
        face = faces[0]
        aligned_face = current_fr.align_face(image, face)
        current_embedding = current_fr.get_face_embedding(aligned_face)
        deepface_embedding = DeepFace.represent(image, model_name="Facenet")[0]["embedding"]
        return current_embedding, deepface_embedding
    return None, None

def verify_face(image):
    faces = current_fr.detect_faces(image)
    if faces:
        face = faces[0]
        aligned_face = current_fr.align_face(image, face)
        current_embedding = current_fr.get_face_embedding(aligned_face)
        deepface_embedding = DeepFace.represent(image, model_name="Facenet")[0]["embedding"]
        
        results = []
        for name, (curr_emb, df_emb) in registered_faces.items():
            current_distance = cosine(current_embedding, curr_emb)
            deepface_distance = cosine(deepface_embedding, df_emb)
            results.append((name, current_distance, deepface_distance))
        
        return min(results, key=lambda x: x[1]) if results else None
    return None

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('register')
def handle_register(data):
    name = data['name']
    image_data = base64.b64decode(data['image'].split(',')[1])
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    current_emb, df_emb = register_face(name, image)
    if current_emb is not None and df_emb is not None:
        registered_faces[name] = (current_emb, df_emb)
        socketio.emit('registration_result', {'success': True, 'name': name})
    else:
        socketio.emit('registration_result', {'success': False, 'name': name})

@socketio.on('verify')
def handle_verify(data):
    image_data = base64.b64decode(data['image'].split(',')[1])
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    start_time = time.time()
    result = verify_face(image)
    end_time = time.time()
    
    if result:
        name, current_distance, deepface_distance = result
        socketio.emit('verification_result', {
            'name': name,
            'current_distance': float(current_distance),
            'deepface_distance': float(deepface_distance),
            'time': (end_time - start_time) * 1000
        })
    else:
        socketio.emit('verification_result', {'name': 'Unknown'})

if __name__ == '__main__':
    socketio.run(app, debug=True)