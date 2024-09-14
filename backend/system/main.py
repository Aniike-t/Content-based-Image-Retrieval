from flask import Flask, request
from flask_cors import CORS
import os
from utils.checkIfImage import is_valid_image
import io

app = Flask(__name__)
CORS(app)

# Define the upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../storage')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return 'No files part', 400
    files = request.files.getlist('files[]')

    if len(files) == 0:
        return 'No selected files', 400

    invalid_files = []
    valid_files = []

    for file in files:
        if file and file.filename != '':
            file_stream = io.BytesIO(file.read())
            file.seek(0)  # Reset file stream position after reading
            if is_valid_image(file_stream):
                valid_files.append(file)
            else:
                invalid_files.append(file.filename)

    # Save valid files
    for file in valid_files:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

    if invalid_files:
        return f'Files uploaded successfully, but the following files were not valid images: {", ".join(invalid_files)}', 200

    return 'Files uploaded successfully', 200

if __name__ == '__main__':
    app.run(debug=True)
