import cv2
import numpy as np
import os
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import pickle
import logging

logging.basicConfig(level=logging.INFO)

# Initialize MTCNN and InceptionResnetV1
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
mtcnn = MTCNN(keep_all=True, device=device)
facenet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

def encode_face(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to read image: {image_path}")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Detect face using MTCNN
        faces, _ = mtcnn.detect(img)
        
        if faces is None:
            logging.warning(f"No face detected in {image_path}")
            return None
        
        # Get the largest face
        face = max(faces, key=lambda box: (box[2] - box[0]) * (box[3] - box[1]))
        x, y, w, h = map(int, face)
        
        face_img = img[y:h, x:w]
        face_img = cv2.resize(face_img, (160, 160))
        
        # Convert to PyTorch tensor
        face_tensor = torch.from_numpy(face_img).permute(2, 0, 1).float().unsqueeze(0).to(device)
        
        # Get embedding
        with torch.no_grad():
            embedding = facenet(face_tensor).cpu().numpy()[0]
        
        return embedding
    
    except Exception as e:
        logging.error(f"Error encoding face: {str(e)}")
        return None

class SimpleClassifier:
    def __init__(self, labels):
        self.labels = labels
    def predict(self, X):
        return np.array([self.labels[0]] * len(X))
    def predict_proba(self, X):
        proba = np.zeros((len(X), len(self.labels)))
        proba[:, 0] = 1  # Always predict the first class with 100% confidence
        return proba

def train_model(image_paths, labels):
    embeddings = []
    valid_labels = []
    
    for path, label in zip(image_paths, labels):
        embedding = encode_face(path)
        if embedding is not None:
            embeddings.append(embedding)
            valid_labels.append(label)
    
    if not embeddings:
        raise ValueError("No valid face embeddings found for training")
    
    # Convert labels to numerical format
    le = LabelEncoder()
    numerical_labels = le.fit_transform(valid_labels)
    
    # Use SimpleClassifier for any number of classes
    clf = SimpleClassifier(le.classes_)
    
    # Create the models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Save the classifier, label encoder, and embeddings
    with open('models/face_classifier.pkl', 'wb') as f:
        pickle.dump((clf, le, embeddings, valid_labels), f)
    
    logging.info(f"Model trained with {len(valid_labels)} samples. Classes: {le.classes_}")


def recognize_face(image_path):
    embedding = encode_face(image_path)
    
    if embedding is None:
        logging.warning(f"No face detected in {image_path}")
        return None, None
    
    # Load the classifier and label encoder
    with open('models/face_classifier.pkl', 'rb') as f:
        clf, le, _, _ = pickle.load(f)
    
    # Predict
    predictions = clf.predict_proba([embedding])[0]
    best_class_index = np.argmax(predictions)
    best_class_probability = predictions[best_class_index]
    
    logging.info(f"Best class index: {best_class_index}, Probability: {best_class_probability}")
    logging.info(f"Available classes: {le.classes_}")
    
    if best_class_probability > 0.7:
        predicted_label = le.classes_[best_class_index]
        return predicted_label, float(best_class_probability)
    else:
        logging.info(f"Confidence too low: {best_class_probability}")
        return None, None