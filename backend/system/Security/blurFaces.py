import cv2
import numpy as np
from mtcnn import MTCNN
from PIL import Image

def blur_faces(image):
    """Detects faces in the image and applies a blur effect."""
    # Initialize MTCNN face detector
    detector = MTCNN()
    
    # Convert PIL Image to NumPy array (OpenCV format)
    image_np = np.array(image)
    
    # Detect faces
    faces = detector.detect_faces(image_np)
    
    # Loop through detected faces
    for face in faces:
        x, y, width, height = face['box']
        # Extract the face region
        face_region = image_np[y:y+height, x:x+width]
        # Blur the face region
        blurred_face = cv2.GaussianBlur(face_region, (99, 99), 30)
        # Replace the face region in the image with the blurred face
        image_np[y:y+height, x:x+width] = blurred_face
    
    # Convert back to PIL Image
    return Image.fromarray(image_np)