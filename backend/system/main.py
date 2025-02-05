from flask import Flask, request, jsonify, g
from flask_cors import CORS
import os
import io
import spacy
import nltk
import threading
import logging
import pandas as pd
from collections import defaultdict
from io import BytesIO
import base64
from PIL import Image
import hashlib
import secrets
import uuid
import sqlite3
from cryptography.fernet import Fernet
import cv2
import numpy as np
import pytesseract


''' Import classes from other files '''
from utils.checkIfImage import is_valid_image
from SQLmethods.connectDB import ConnectDB
from SQLmethods.connectDB import get_db_manager
from methods.getColors import ImageColorAnalyzer
from methods.getMetadata import GetMetadata
from methods.getFeaturesCNN import ImageFeatureExtractor
from ThreadPool.ImageProcessorManager import ImageProcessingManager
from tokenisation.wordnetExtraction import process_top_features
from tokenisation.SentenceConv import SentenceConverter
from tokenisation.SQLqueryGenerator import SQLQueryGenerator
from Retrieval.RetrieveAlgo import VectorSpaceModel
from Security.hashImage import calculate_file_hash
# from Security.blurFaces import blur_faces


# Initialize Flask app and CORS
app = Flask(__name__)

# Get database connection and cursor
cursor, conn = ConnectDB()
db_manager = get_db_manager()

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../storage')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Process Manager Initialization
image_manager = ImageProcessingManager(
    upload_folder=UPLOAD_FOLDER,
    ImageColorAnalyzer=ImageColorAnalyzer,
    GetMetadata=GetMetadata,
    ImageFeatureExtractor =ImageFeatureExtractor,
    process_top_features =process_top_features,
    cursor = cursor,
    conn = conn
)
# Store processing errors
processing_errors = []


def store_filename_and_hash(db_manager, filename, filehash, uuid):
    """Store the filename, filehash, and UUID in the ImageHashes table."""
    sql = "INSERT INTO ImageHashes (filename, filehash, uuid) VALUES (?, ?, ?)"
    db_manager.execute_query(sql, (filename, filehash, uuid))









def blur_faces(image):
    image_np = np.array(image)
    gray_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    for (x, y, w, h) in faces:
        face_region = image_np[y:y+h, x:x+w]
        blurred_face = cv2.GaussianBlur(face_region, (99, 99), 30)
        image_np[y:y+h, x:x+w] = blurred_face
    return Image.fromarray(image_np)

def blur_text(image):
    # Convert the PIL image to a NumPy array
    image_np = np.array(image)
    
    # Convert the image to grayscale for text detection
    gray_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    
    # Apply bilateral filter and find edges
    bfilter = cv2.bilateralFilter(gray_image, 11, 17, 17)
    edged = cv2.Canny(bfilter, 30, 200)

    # Find contours
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Prepare a mask for blurring
    mask = np.zeros_like(image_np)

    # Loop through contours to find bounding rectangles and blur them
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.015 * perimeter, True)
        if len(approx) == 4:  # Assuming a rectangular shape
            x, y, w, h = cv2.boundingRect(contour)
            roi = image_np[y:y+h, x:x+w]
            blurred_roi = cv2.GaussianBlur(roi, (21, 21), 0)  # Increased blur
            image_np[y:y+h, x:x+w] = blurred_roi  # Replace original ROI with blurred ROI
            
            # Optionally draw on the mask to visualize the blurring area
            cv2.fillPoly(mask, [approx], (255, 255, 255))

    # Combine the original image with the blurred area
    result = cv2.bitwise_and(image_np, mask) + cv2.bitwise_and(image_np, ~mask)

    # Convert back to PIL image
    return Image.fromarray(result)










def save_valid_files(files, uuid, face_blur_enabled, text_blur_enabled):
    """
    Save valid image files to the upload folder and return the valid and invalid files.
    """
    valid_files = []
    invalid_files = []
    for file in files:
        if file and file.filename:
            file_stream = io.BytesIO(file.read())
            file.seek(0)

            if is_valid_image(file_stream):
                valid_files.append(file)
            else:
                invalid_files.append(file.filename)

    # Save valid files and blur faces and/or text if enabled
    for file in valid_files:
        file.seek(0)
        image = Image.open(file)
        if face_blur_enabled:  # Check if face blur is enabled
            image = blur_faces(image)
        if text_blur_enabled:  # Check if text blur is enabled
            image = blur_text(image)

        image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        image.save(image_path)

        file_stream = io.BytesIO(file.read())
        file_stream.seek(0)
        file_hash = calculate_file_hash(file_stream)
        store_filename_and_hash(db_manager, image_path, file_hash, uuid)

    return valid_files, invalid_files





@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files part'}), 400

    files = request.files.getlist('files[]')
    uuid = request.form.get('uuid')
    face_blur_enabled = request.form.get('faceBlur') == 'true'  # Get face blur option as boolean
    text_blur_enabled = request.form.get('textBlur') == 'true'  # Get text blur option as boolean

    if not uuid:
        return jsonify({'error': 'UUID not provided.'}), 400

    if not files:
        return jsonify({'error': 'No selected files'}), 400

    valid_files, invalid_files = save_valid_files(files, uuid, face_blur_enabled, text_blur_enabled)

    def process_files_in_background(valid_files):
        global processing_errors
        processing_errors = []
        for file in valid_files:
            try:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                image_manager.process_image(file_path)
            except Exception as e:
                logging.error(f"Error processing {file.filename}: {str(e)}")
                processing_errors.append({'file': file.filename, 'error': str(e)})

        image_manager.wait_for_completion()

    background_thread = threading.Thread(target=process_files_in_background, args=(valid_files,))
    background_thread.start()

    return jsonify({
        'message': 'Files are being processed in the background',
        'invalid_files': invalid_files,
        'valid_files': [file.filename for file in valid_files]
    }), 200


@app.route('/processing_errors', methods=['GET'])
def get_processing_errors():
    """
    Returns any errors that occurred during image processing for frontend notifications.
    """
    global processing_errors

    if processing_errors:
        return jsonify({
            'message': 'Some images could not be processed',
            'errors': processing_errors
        }), 200

    return jsonify({'message': 'No errors occurred during processing'}), 200


@app.route('/search', methods=['POST'])
def search_images():
    """
    Handle image search requests based on the query and user UUID.
    """
    # Get JSON data from the request
    data = request.get_json()

    # Extract the query and UUID from the incoming request
    query = data.get('query', '')
    uuid = data.get('uuid', '')

    if not query:
        return jsonify({'error': 'Query is required.'}), 400

    try:
        # Call the get_query_results function with the user query
        filenames = get_query_results(sentence=query)

        # Prepare a list to hold low-quality images
        low_quality_images = []

        for filename in filenames:
            # Check if the filename is associated with the UUID
            # if not is_filename_associated_with_uuid(filename, uuid):
            #     continue  # Skip if not associated

            # Open the original image
            with Image.open(filename) as img:
                # Create a BytesIO object to hold the low-quality image
                buffered = BytesIO()

                # Resize the image and save it to the BytesIO object
<<<<<<< HEAD
<<<<<<< HEAD
                img = img.resize((img.width, img.height))  # Resize to 25% of original
                img.save(buffered, format='JPEG', quality=100)
=======
                img = img.resize(img.width , img.height )  # Resize to 25% of original
                img.save(buffered, format='JPEG', quality=20)
>>>>>>> parent of c36b9f5 (+word convertor fix)
=======
                img = img.resize(img.width , img.height )  # Resize to 25% of original
                img.save(buffered, format='JPEG', quality=20)
>>>>>>> parent of c36b9f5 (+word convertor fix)

                # Get the binary data from the BytesIO object
                low_quality_image_data = buffered.getvalue()

                # Encode the binary data to base64
                low_quality_image_base64 = base64.b64encode(low_quality_image_data).decode('utf-8')

                # Append the base64 data to the list
                low_quality_images.append(low_quality_image_base64)

        return jsonify({'images': low_quality_images}), 200

    except Exception as e:
        logging.error(f"Error retrieving images: {str(e)}")
        return jsonify({'error': 'Failed to fetch images. Please try again.'}), 500



def is_filename_associated_with_uuid(filename, uuid):
    """
    Check if the filename is associated with the given UUID.
    """
    sql = "SELECT COUNT(*) FROM ImageHashes WHERE filename = ? AND uuid = ?"
    result = get_db_manager().fetch_query_results(sql, (filename, uuid))
    print(filename, uuid)
    print(result)
    return result[0][0] > 0 if result else False



''' Query Processing logic'''
def get_query_results(sentence):
    """
    Processes the sentence to fetch image filenames based on the query.
    """
    converter = SentenceConverter()
    result = converter.convert_to_query(sentence)
    print(result)
    query_generator = SQLQueryGenerator(result)
    sql_query, included_words = query_generator.generate_query()
    print(sql_query)
    print(included_words)
    sql_query_result = get_db_manager().fetch_query_results(sql_query)

    vsm = VectorSpaceModel(sql_query_result, included_words)
    sorted_vector_df = vsm.get_sorted_vector_df()

    filenames = sorted_vector_df.index.tolist()

    print(filenames)
    return filenames



def get_db_connection():
    if 'db_connection' not in g:
        g.db_connection = sqlite3.connect('../database.db')
        g.db_connection.row_factory = sqlite3.Row
    return g.db_connection

@app.teardown_appcontext
def close_db(exception=None):
    if 'db_connection' in g:
        g.db_connection.close()
        del g.db_connection

@app.route('/signup', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Invalid input"}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user_uuid = str(uuid.uuid4())
    random_salt = secrets.token_urlsafe(16)
    unique_key = f"{random_salt}-{user_uuid}"

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        insert_query = "INSERT INTO users (username, hashed_password, uuid, unique_key) VALUES (?, ?, ?, ?)"
        cursor.execute(insert_query, (username, hashed_password, user_uuid, unique_key))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400
    finally:
        conn.close()

    return jsonify({"message": "Registration successful"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Invalid input"}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT uuid FROM users WHERE username = ? AND hashed_password = ?", (username, hashed_password))
        user = cursor.fetchone()

        if user:
            return jsonify({"token": user['uuid']}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    finally:
        conn.close()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response



if __name__ == '__main__':
    app.run(debug=True)