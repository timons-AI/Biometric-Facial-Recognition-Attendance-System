import tensorflow as tf
import cv2
import numpy as np
from scipy.spatial.distance import cosine
import logging
from config import Config

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
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.load_facenet_model()

    def load_facenet_model(self):
        try:
            # Create a new graph and set it as the default
            self.graph = tf.Graph()
            with self.graph.as_default():
                # Load the graph def from the file
                with tf.io.gfile.GFile(Config.FACENET_MODEL_PATH, "rb") as f:
                    graph_def = tf.compat.v1.GraphDef()
                    graph_def.ParseFromString(f.read())
                
                # Import the graph def into the current graph
                tf.import_graph_def(graph_def, name='')
            
            # Create a session for the loaded graph
            self.sess = tf.compat.v1.Session(graph=self.graph)
            
            # Get input and output tensors
            self.images_placeholder = self.graph.get_tensor_by_name("input:0")
            self.embeddings = self.graph.get_tensor_by_name("embeddings:0")
            self.phase_train_placeholder = self.graph.get_tensor_by_name("phase_train:0")

            logger.info("FaceNet model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading FaceNet model: {e}")
            return None

    def preprocess_face(self, face_image):
        face_image = cv2.resize(face_image, (160, 160))
        face_image = face_image.astype(np.float32) / 255.0  # Normalize to [0,1]
        return face_image

    def get_face_embedding(self, face_image):
        try:
            if self.sess is None:
                logger.error("TensorFlow session is not initialized")
                return None

            preprocessed_image = self.preprocess_face(face_image)
            feed_dict = {
                self.images_placeholder: [preprocessed_image],
                self.phase_train_placeholder: False
            }
            face_embedding = self.sess.run(self.embeddings, feed_dict=feed_dict)[0]
            return face_embedding
        except Exception as e:
            logger.error(f"Error getting face embedding: {e}")
            return None

    def compare_faces(self, face_embedding1, face_embedding2, threshold=0.7):
        distance = cosine(face_embedding1, face_embedding2)
        return distance < threshold

    def detect_faces(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return faces

    def is_valid_face(self, face_image):
        # Add more sophisticated checks here if needed
        return face_image.shape[0] > 50 and face_image.shape[1] > 50