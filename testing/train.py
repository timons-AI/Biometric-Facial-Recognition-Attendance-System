from flask import Flask, request, jsonify
import numpy as np
import cv2
from mtcnn import MTCNN
from keras_facenet import FaceNet
import pickle

app = Flask(__name__)

# Initialize MTCNN face detector
detector = MTCNN()

# Initialize FaceNet model
embedder = FaceNet()

# Load known faces and embeddings
with open('known_faces.pkl', 'rb') as f:
    known_faces = pickle.load(f)

def get_face_embedding(image):
    results = detector.detect_faces(image)
    if len(results) == 0:
        return None
    
    x, y, width, height = results[0]['box']
    face = image[y:y+height, x:x+width]
    face = cv2.resize(face, (160, 160))
    face = face.astype('float32')
    mean, std = face.mean(), face.std()
    face = (face - mean) / std

    embedding = embedder.embeddings([face])[0]
    return embedding

@app.route('/recognize', methods=['POST'])
def recognize():
    file = request.files['image']
    npimg = np.fromstring(file.read(), np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    
    embedding = get_face_embedding(img)
    if embedding is None:
        return jsonify({"error": "No face detected"}), 400
    
    distances = np.linalg.norm(known_faces['embeddings'] - embedding, axis=1)
    min_distance = np.min(distances)
    if min_distance < 0.6:  # Threshold for recognition
        idx = np.argmin(distances)
        name = known_faces['names'][idx]
        return jsonify({"name": name})
    else:
        return jsonify({"error": "Unknown face"}), 404

if __name__ == '__main__':
    app.run(debug=True)
