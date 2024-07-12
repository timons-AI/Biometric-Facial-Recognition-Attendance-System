import tensorflow as tf
import cv2
import numpy as np
from scipy.spatial.distance import cosine
import logging
from mtcnn import MTCNN
from PIL import Image
import io
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovedFaceRecognition:
    _instance = None

    @staticmethod
    def get_instance():
        if ImprovedFaceRecognition._instance is None:
            ImprovedFaceRecognition._instance = ImprovedFaceRecognition()
        return ImprovedFaceRecognition._instance

    def __init__(self):
        self.graph = None
        self.sess = None
        self.images_placeholder = None
        self.embeddings = None
        self.phase_train_placeholder = None
        self.face_detector = MTCNN(min_face_size=20, steps_threshold=[0.6, 0.7, 0.7])
        self.load_facenet_model()

    def load_facenet_model(self):
        try:
            with tf.io.gfile.GFile("path/to/your/facenet_model.pb", "rb") as f:
                graph_def = tf.compat.v1.GraphDef()
                graph_def.ParseFromString(f.read())
            
            self.graph = tf.Graph()
            with self.graph.as_default():
                tf.import_graph_def(graph_def, name='')
            
            self.sess = tf.compat.v1.Session(graph=self.graph)
            self.images_placeholder = self.graph.get_tensor_by_name("input:0")
            self.embeddings = self.graph.get_tensor_by_name("embeddings:0")
            self.phase_train_placeholder = self.graph.get_tensor_by_name("phase_train:0")
            
            logger.info("FaceNet model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading FaceNet model: {e}")

    def preprocess_image(self, image_data):
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
            image_data = base64.b64decode(image_data)
        
        if isinstance(image_data, bytes):
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif isinstance(image_data, np.ndarray):
            image = image_data
        else:
            raise ValueError("Unsupported image data type")
        
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def detect_faces(self, image):
        faces = self.face_detector.detect_faces(image)
        return [face['box'] for face in faces]

    def align_face(self, image, face_box):
        x, y, w, h = face_box
        face_img = image[y:y+h, x:x+w]
        return cv2.resize(face_img, (160, 160))

    def get_face_embedding(self, face_image):
        face_image = face_image.astype(np.float32) / 255.0
        feed_dict = {
            self.images_placeholder: [face_image],
            self.phase_train_placeholder: False
        }
        return self.sess.run(self.embeddings, feed_dict=feed_dict)[0]

    def compare_faces(self, known_embedding, unknown_embedding, threshold=0.7):
        distance = cosine(known_embedding, unknown_embedding)
        return distance < threshold, distance

    def recognize_face(self, image_data, stored_embeddings, threshold=0.7):
        image = self.preprocess_image(image_data)
        faces = self.detect_faces(image)
        
        if not faces:
            return None, None
        
        face_image = self.align_face(image, faces[0])
        face_embedding = self.get_face_embedding(face_image)
        
        best_match = None
        best_distance = float('inf')
        
        for student_id, embeddings in stored_embeddings.items():
            for embedding in embeddings:
                is_match, distance = self.compare_faces(embedding, face_embedding, threshold)
                if is_match and distance < best_distance:
                    best_match = student_id
                    best_distance = distance
        
        return best_match, best_distance

    def register_face(self, image_data):
        image = self.preprocess_image(image_data)
        faces = self.detect_faces(image)
        
        if not faces:
            return None
        
        face_image = self.align_face(image, faces[0])
        face_embedding = self.get_face_embedding(face_image)
        
        return face_embedding.tolist()
