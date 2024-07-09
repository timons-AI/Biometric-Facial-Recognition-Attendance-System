import tensorflow as tf
import cv2
import numpy as np
from scipy.spatial.distance import cosine
import logging
from config import Config
from mtcnn import MTCNN
from PIL import Image
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceRecognition:
    _instance = None

    @staticmethod
    def get_instance():
        if FaceRecognition._instance is None:
            FaceRecognition._instance = FaceRecognition()
        return FaceRecognition._instance

    def __init__(self):
        if FaceRecognition._instance is not None:
            raise Exception("This class is a singleton. Use get_instance() to get the object.")
        else:
            FaceRecognition._instance = self
            self.graph = None
            self.sess = None
            self.images_placeholder = None
            self.embeddings = None
            self.phase_train_placeholder = None
            self.face_detector = MTCNN(min_face_size=20, steps_threshold=[0.6, 0.7, 0.7])
            self.load_facenet_model()

    def load_facenet_model(self):
        try:
            self.graph = tf.Graph()
            with self.graph.as_default():
                with tf.io.gfile.GFile(Config.FACENET_MODEL_PATH, "rb") as f:
                    graph_def = tf.compat.v1.GraphDef()
                    graph_def.ParseFromString(f.read())
                tf.import_graph_def(graph_def, name='')
            
            self.sess = tf.compat.v1.Session(graph=self.graph)
            
            self.images_placeholder = self.graph.get_tensor_by_name("input:0")
            self.embeddings = self.graph.get_tensor_by_name("embeddings:0")
            self.phase_train_placeholder = self.graph.get_tensor_by_name("phase_train:0")
            
            logger.info("FaceNet model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading FaceNet model: {e}")
            return None

    def detect_faces(self, frame):
        logger.info(f"Detecting faces in frame of shape {frame.shape}")
        faces = self.face_detector.detect_faces(frame)
        logger.info(f"Detected {len(faces)} faces")
        if len(faces) == 0:
            logger.warning("No faces detected. Saving debug image.")
            cv2.imwrite('debug_no_faces.jpg', frame)
        return faces

    def align_face(self, image, face):
        logger.debug(f"Aligning face: {face}")
        bounding_box = face['box']
        keypoints = face['keypoints']
        
        left_eye = keypoints['left_eye']
        right_eye = keypoints['right_eye']
        
        # Calculate angle
        dY = right_eye[1] - left_eye[1]
        dX = right_eye[0] - left_eye[0]
        angle = np.degrees(np.arctan2(dY, dX)) - 180

        # Get the center of the face
        center = (bounding_box[0] + bounding_box[2]//2, bounding_box[1] + bounding_box[3]//2)
        
        # Rotate the image
        M = cv2.getRotationMatrix2D(center, angle, 1)
        aligned_image = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]), flags=cv2.INTER_CUBIC)
        
        # Extract the face
        (x, y, w, h) = bounding_box
        face_img = aligned_image[y:y+h, x:x+w]
        logger.debug(f"Aligned face shape: {face_img.shape}")
        
        return cv2.resize(face_img, (160, 160))

    def preprocess_face(self, face_image):
        face_image = face_image.astype(np.float32) / 255.0
        return face_image

    def get_face_embedding(self, face_image):
        logger.debug(f"Getting face embedding for image of shape {face_image.shape}")
        try:
            if self.sess is None:
                logger.error("TensorFlow session is not initialized")
                return None
            preprocessed_image = self.preprocess_face(face_image)
            logger.debug(f"Preprocessed image shape: {preprocessed_image.shape}")
            feed_dict = {
                self.images_placeholder: [preprocessed_image],
                self.phase_train_placeholder: False
            }
            face_embedding = self.sess.run(self.embeddings, feed_dict=feed_dict)[0]
            logger.debug(f"Face embedding shape: {face_embedding.shape}")
            return face_embedding
        except Exception as e:
            logger.error(f"Error getting face embedding: {e}")
            return None

    def compare_faces(self, face_embedding1, face_embedding2, threshold=0.7):
        distance = cosine(face_embedding1, face_embedding2)
        return distance < threshold

    def is_valid_face(self, face_image):
        if face_image.shape[0] < 50 or face_image.shape[1] < 50:
            return False
        
        # Check for blur
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        blur_value = cv2.Laplacian(gray, cv2.CV_64F).var()
        if blur_value < 100:  # Adjust this threshold as needed
            return False
        
        # Check for extreme lighting conditions
        if np.mean(gray) < 50 or np.mean(gray) > 200:
            return False
        
        return True

    def get_multiple_embeddings(self, face_image, num_augmentations=5):
        embeddings = []
        
        # Original image
        embeddings.append(self.get_face_embedding(face_image))
        
        # Augmented images
        for _ in range(num_augmentations - 1):
            augmented_image = self.augment_image(face_image)
            embedding = self.get_face_embedding(augmented_image)
            if embedding is not None:
                embeddings.append(embedding)
        
        return embeddings

    def augment_image(self, image):
        # Apply random augmentations
        augmented = image.copy()
        
        # Random brightness adjustment
        brightness = random.uniform(0.8, 1.2)
        augmented = cv2.convertScaleAbs(augmented, alpha=brightness, beta=0)
        
        # Random contrast adjustment
        contrast = random.uniform(0.8, 1.2)
        augmented = cv2.convertScaleAbs(augmented, alpha=contrast, beta=0)
        
        # Random rotation
        angle = random.uniform(-15, 15)
        h, w = augmented.shape[:2]
        M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)
        augmented = cv2.warpAffine(augmented, M, (w, h))
        
        return augmented

    def recognize_face(self, input_embedding, stored_embeddings, threshold=0.6):
        if not stored_embeddings:
            return False
        distances = [cosine(input_embedding, emb) for emb in stored_embeddings]
        min_distance = min(distances)
        return min_distance < threshold

    def register_face(self, face_image):
        if not self.is_valid_face(face_image):
            return None
        
        aligned_face = self.align_face(face_image, self.detect_faces(face_image)[0])
        embeddings = self.get_multiple_embeddings(aligned_face, num_augmentations=10)
        return embeddings

    def verify_face(self, face_image, stored_embeddings):
        if not self.is_valid_face(face_image):
            return False
        
        aligned_face = self.align_face(face_image, self.detect_faces(face_image)[0])
        input_embedding = self.get_face_embedding(aligned_face)
        
        return self.recognize_face(input_embedding, stored_embeddings)