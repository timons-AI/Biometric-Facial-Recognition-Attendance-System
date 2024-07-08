import os
import cv2
import numpy as np
import tensorflow as tf
from mtcnn import MTCNN
from keras_facenet import FaceNet
import pickle

# Initialize MTCNN face detector
detector = MTCNN()

# Initialize FaceNet model
embedder = FaceNet()

dataset_path = "path/to/dataset"
known_faces = {'names': [], 'embeddings': []}

def get_face_embedding(image):
    # Detect faces in the image
    results = detector.detect_faces(image)
    if len(results) == 0:
        return None
    
    # Get the bounding box of the first face
    x, y, width, height = results[0]['box']
    face = image[y:y+height, x:x+width]
    
    # Resize and preprocess the face
    face = cv2.resize(face, (160, 160))
    face = face.astype('float32')
    mean, std = face.mean(), face.std()
    face = (face - mean) / std

    # Get the embedding
    embedding = embedder.embeddings([face])[0]
    return embedding

for student_dir in os.listdir(dataset_path):
    student_path = os.path.join(dataset_path, student_dir)
    if not os.path.isdir(student_path):
        continue
    
    for image_name in os.listdir(student_path):
        image_path = os.path.join(student_path, image_name)
        image = cv2.imread(image_path)
        embedding = get_face_embedding(image)
        if embedding is not None:
            known_faces['names'].append(student_dir)
            known_faces['embeddings'].append(embedding)

# Save the known faces and embeddings
with open('known_faces.pkl', 'wb') as f:
    pickle.dump(known_faces, f)
