from flask import Flask, request, jsonify
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


# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app)

# Get database connection and cursor
cursor, conn = ConnectDB()
db_manager = get_db_manager

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




def save_valid_files(files):
    """
    Save valid image files to the upload folder and return the valid and invalid files.
    """
    valid_files = []
    invalid_files = []
    for file in files:
        if file and file.filename:
            file_stream = io.BytesIO(file.read())
            file.seek(0)  # Reset file stream position after reading

            if is_valid_image(file_stream):
                valid_files.append(file)
            else:
                invalid_files.append(file.filename)

    # Save valid files
    for file in valid_files:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

    return valid_files, invalid_files




@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file uploads and process them using ImageProcessingManager.
    """
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files part'}), 400
    files = request.files.getlist('files[]')
    if not files:
        return jsonify({'error': 'No selected files'}), 400
    # Save valid files
    valid_files, invalid_files = save_valid_files(files)
    
    def process_files_in_background(valid_files):
        global processing_errors
        processing_errors = []  # Clear errors before each batch

        # Process valid images
        for file in valid_files:
            try:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                image_manager.process_image(file_path)  # Pass the full file path
            except Exception as e:
                # Log the error and store it for frontend notification
                logging.error(f"Error processing {file.filename}: {str(e)}")
                processing_errors.append({'file': file.filename, 'error': str(e)})
        # Wait for all threads to finish processing
        image_manager.wait_for_completion()
        
    # Run processing in a background thread
    background_thread = threading.Thread(target=process_files_in_background, args=(valid_files,))
    background_thread.start()
    # Return a response immediately
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
    Handle image search requests based on the query.
    """
    # Get JSON data from the request
    data = request.get_json()

    # Extract the query from the incoming request
    query = data.get('query', '')

    if not query:
        return jsonify({'error': 'Query is required.'}), 400

    try:
        # Call the get_query_results function with the user query
        filenames = get_query_results(sentence=query)

        # Prepare a list to hold low-quality images
        low_quality_images = []

        for filename in filenames:
            # Open the original image
            with Image.open(filename) as img:
                # Create a BytesIO object to hold the low-quality image
                buffered = BytesIO()

                # Resize the image and save it to the BytesIO object
                img = img.resize(img.width , img.height )  # Resize to 25% of original
                img.save(buffered, format='JPEG', quality=20)

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



if __name__ == '__main__':
    app.run(debug=True)