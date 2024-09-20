from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import io
from utils.checkIfImage import is_valid_image
from SQLmethods.connectDB import ConnectDB
from methods.getColors import ImageColorAnalyzer
from methods.getMetadata import GetMetadata
from methods.getFeaturesCNN import ImageFeatureExtractor
from ThreadPool.ImageProcessorManager import ImageProcessingManager
from tokenisation.wordnetExtraction import process_top_features

# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../storage')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Process Manager Initialization
image_manager = ImageProcessingManager(
    upload_folder=UPLOAD_FOLDER,
    ImageColorAnalyzer=ImageColorAnalyzer,
    GetMetadata=GetMetadata,
    ImageFeatureExtractor=ImageFeatureExtractor,
    process_top_features =process_top_features
)

# Get database connection and cursor
c, conn = ConnectDB()

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

    # Process valid images
    for file in valid_files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        image_manager.process_image(file_path)  # Pass the full file path

    # Wait for all threads to finish processing
    image_manager.wait_for_completion()

    return jsonify({
        'message': 'Files processed successfully',
        'invalid_files': invalid_files,
        'valid_files': [file.filename for file in valid_files]
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
