# --- START OF FILE main.py ---
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import io
import logging
import base64
from PIL import Image
from io import BytesIO
import threading
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
import re

''' Import classes from other files '''
from utils.checkIfImage import is_valid_image
from SQLmethods.connectDB import ConnectDB, get_db_manager
from methods.getColors import ImageColorAnalyzer
from methods.getMetadata import GetMetadata
from methods.getFeaturesCNN import ImageFeatureExtractor
from ThreadPool.ImageProcessorManager import ImageProcessingManager
from tokenisation.wordnetExtraction import process_top_features
from tokenisation.SentenceConv import SentenceConverter
from Retrieval.RetrieveAlgo import VectorSpaceModel

# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app)

# NLTK Downloads (Ensure these are downloaded)
nltk.download('stopwords')
nltk.download('punkt')

# Get database connection and cursor (ensure correct path)
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
    ImageFeatureExtractor=ImageFeatureExtractor,
    process_top_features=process_top_features,
    cursor=cursor,
    conn=conn
)

# Store processing errors
processing_errors = []

def save_valid_files(files):
    """
    Save valid image files (only base filenames).
    """
    valid_files = []
    invalid_files = []
    for file in files:
        if file and file.filename:
            file_stream = io.BytesIO(file.read())
            file.seek(0)  # Rewind the file stream
            if is_valid_image(file_stream):
                valid_files.append(file)
            else:
                invalid_files.append(file.filename)
    for file in valid_files:
        base_filename = os.path.basename(file.filename)
        file.seek(0)  # Rewind again before saving
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], base_filename))
    return valid_files, invalid_files

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles file uploads."""
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files part'}), 400
    files = request.files.getlist('files[]')
    if not files:
        return jsonify({'error': 'No selected files'}), 400

    valid_files, invalid_files = save_valid_files(files)

    def process_files_in_background(valid_files):
        global processing_errors
        processing_errors = []  # Clear previous errors
        for file in valid_files:
            try:
                base_filename = os.path.basename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], base_filename)
                image_manager.process_image(base_filename)  # Pass only base filename
            except Exception as e:
                logging.error(f"Error processing {file.filename}: {str(e)}")
                processing_errors.append({'file': file.filename, 'error': str(e)})
        image_manager.wait_for_completion()

    background_thread = threading.Thread(target=process_files_in_background, args=(valid_files,))
    background_thread.start()

    return jsonify({
        'message': 'Files are being processed in the background',
        'invalid_files': invalid_files,
        'valid_files': [os.path.basename(file.filename) for file in valid_files]  # Return base filenames
    }), 200

@app.route('/processing_errors', methods=['GET'])
def get_processing_errors():
    """Returns processing errors."""
    global processing_errors
    if processing_errors:
        return jsonify({'message': 'Some images could not be processed', 'errors': processing_errors}), 200
    return jsonify({'message': 'No errors occurred during processing'}), 200

@app.route('/search', methods=['POST'])
def search_images():
    """Handles image search requests."""
    data = request.get_json()
    query = data.get('query', '')
    if not query:
        return jsonify({'error': 'Query is required.'}), 400

    try:
        filenames = get_query_results(query)  # Use the updated function
        low_quality_images = []
        image_filenames = []
        for filename in filenames:
            try:
                with Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename)) as img:
                    buffered = BytesIO()
                    img.save(buffered, format='JPEG')  # Save as JPEG (consistent format)
                    image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    low_quality_images.append(image_base64)
                    image_filenames.append(filename)
            except FileNotFoundError:
                logging.warning(f"Image file not found: {filename}")
                # Handle missing file gracefully (e.g., skip, or return a placeholder)
                continue
            except Exception as e:
                logging.error(f"Error processing image {filename}: {e}")
                continue  # Continue to the next image

        return jsonify({'images': low_quality_images, 'filenames': image_filenames}), 200

    except Exception as e:
        logging.error(f"Error retrieving images: {str(e)}")
        return jsonify({'error': 'Failed to fetch images. Please try again.'}), 500


# --- KEPT THE ORIGINAL FEEDBACK METHOD ---
@app.route('/feedback', methods=['POST'])
def handle_feedback():
    """Handles user feedback."""
    data = request.get_json()
    filename = data.get('filename')
    feedback = data.get('feedback')
    query = data.get('query')
    if not filename or not feedback or not query:
        return jsonify({'error': 'Missing data'}), 400

    try:
        update_probabilities(filename, feedback, query)
        return jsonify({'message': 'Feedback received'}), 200
    except Exception as e:
        logging.error(f"Error handling feedback: {str(e)}")
        return jsonify({'error': 'Failed to process feedback'}), 500

def update_probabilities(filename, feedback, query):
    """Updates probabilities based on feedback."""
    db_manager = get_db_manager()
    base_filename = os.path.basename(filename)

    # --- Simplified Query Processing (for feedback) ---
    converter = SentenceConverter()
    processed_query = converter.convert_to_query(query)  # Use SentenceConverter
    included_words = [word.split()[0] for word in processed_query.split() if not word.startswith("-")] # Extract the words
    # -------------------------------------------------

    placeholders = ', '.join(['?'] * len(included_words))
    where_clause = f"filename LIKE ? AND feature_value IN ({placeholders})"

    current_features = db_manager.fetch_query_results(
        f"SELECT feature_value, probability FROM Imagefeatures WHERE {where_clause}",
        ('%' + base_filename, *included_words)
    )

    if not current_features:
        print(f"Warning: No matching features found for {filename}, query: {query}")
        return

    for feature_value, probability in current_features:
        probability = float(probability)
        new_probability = min(probability * 1.2, 1.0) if feedback == "positive" else max(probability * 0.8, 0.0)
        print(f"Updating probability for {filename}, {feature_value} from {probability} to {new_probability}")
        db_manager.execute_query(
            "UPDATE Imagefeatures SET probability = ? WHERE filename LIKE ? AND feature_value = ?",
            (new_probability, filename, feature_value)
        )
# --- END OF ORIGINAL FEEDBACK METHOD ---


def get_query_results(sentence):
    """
    Processes the sentence and fetches image filenames.
    Uses SentenceConverter for query processing and VectorSpaceModel for retrieval.
    """
    converter = SentenceConverter()
    processed_query = converter.convert_to_query(sentence)
    included_words = [word.split()[0] for word in processed_query.split() if not word.startswith("-")]

    vsm = VectorSpaceModel(db_manager, included_words, sentence)
    sorted_vector_df = vsm.get_sorted_vector_df()

    # Get base filenames, ensuring they exist in the upload folder.
    filenames = []
    for full_path in sorted_vector_df.index.tolist():
        base_filename = os.path.basename(full_path)
        if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], base_filename)):
            filenames.append(base_filename)
        else:
            logging.warning(f"File not found in upload folder: {base_filename}") # Log missing files

    return filenames


@app.route('/user_sentence', methods=['POST'])
def handle_user_sentence():
    data = request.get_json()
    filename = data.get('filename')
    sentence = data.get('sentence')

    if not filename or not sentence:
        return jsonify({'error': 'Missing filename or sentence'}), 400

    try:
        db_manager = get_db_manager()
        base_filename = os.path.basename(filename)

        # Store the sentence in UserSentences table
        db_manager.execute_query(
            "INSERT INTO UserSentences (filename, sentence) VALUES (?, ?)",
            (base_filename, sentence)
        )

        # Check if sentence count exceeds threshold
        sentence_count = db_manager.fetch_query_results(
            "SELECT COUNT(*) FROM UserSentences WHERE filename = ?",
            (base_filename,)
        )[0][0]

        if sentence_count >= 4:
            process_user_sentences(base_filename)

        return jsonify({'message': 'Sentence received and processed'}), 200

    except Exception as e:
        logging.error(f"Error handling user sentence: {str(e)}")
        return jsonify({'error': 'Failed to process sentence'}), 500


def process_user_sentences(filename):
    """Processes user sentences to extract keywords and update Imagefeatures."""
    db_manager = get_db_manager()

    # Fetch all sentences for the given filename
    sentences = db_manager.fetch_query_results(
        "SELECT sentence FROM UserSentences WHERE filename = ?",
        (filename,)
    )
    sentences = [s[0] for s in sentences]  # Extract sentences from the result

    # Combine sentences and preprocess
    combined_text = ' '.join(sentences)
    keywords, tfidf_scores = extract_keywords_with_tfidf(combined_text)

    # Delete existing user sentence feedback entries for the filename
    db_manager.execute_query(
        "DELETE FROM Imagefeatures WHERE filename = ? AND feature_type = 'User sentence feedback'",
        (filename,)
    )

    # Insert the new keywords and their TF-IDF scores as probabilities
    for keyword, score in zip(keywords, tfidf_scores):
        db_manager.execute_query(
            "INSERT INTO Imagefeatures (filename, feature_type, feature_value, probability) VALUES (?, 'User sentence feedback', ?, ?)",
            (filename, keyword, score)
        )

def extract_keywords_with_tfidf(text):
    """
    Extracts keywords from the given text using TF-IDF.

    Args:
        text: The input text.

    Returns:
        A tuple containing:
          - A list of keywords.
          - A list of corresponding TF-IDF scores.
    """
    # 1. Preprocessing
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation

    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text)
    filtered_tokens = [w for w in tokens if not w in stop_words and len(w) > 2] # Remove stopwords and short words

    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(w) for w in filtered_tokens]

    # 2. TF-IDF Calculation
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([' '.join(stemmed_tokens)])  # Join back for TF-IDF
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray()[0]  # Get scores for the single document


    # 3. Keyword Selection (Top N)
    top_n = 10 # Number of keywords
    # Sort indices by TF-IDF score in descending order
    sorted_indices = tfidf_scores.argsort()[-top_n:][::-1]
    keywords = [feature_names[i] for i in sorted_indices]
    scores = [tfidf_scores[i] for i in sorted_indices]
    return keywords, scores

# New route to get all images
@app.route('/all_images', methods=['GET'])
def get_all_images():
    try:
        image_files = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
        images_data = []
        filenames = []

        for filename in image_files:
            try:
                with Image.open(os.path.join(UPLOAD_FOLDER, filename)) as img:
                    buffered = BytesIO()
                    img.save(buffered, format='JPEG')
                    image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    images_data.append(image_base64)
                    filenames.append(filename)
            except (FileNotFoundError, OSError) as e: # Catch OSError for non-image files
                logging.warning(f"Could not open or read image file: {filename} - {e}")
                continue  # Skip to the next file
            except Exception as e:
                logging.error(f"Error processing image {filename}: {e}")
                continue

        return jsonify({'images': images_data, 'filenames': filenames}), 200

    except Exception as e:
        logging.error(f"Error retrieving all images: {str(e)}")
        return jsonify({'error': 'Failed to fetch all images'}), 500


if __name__ == '__main__':
    app.run(debug=True)