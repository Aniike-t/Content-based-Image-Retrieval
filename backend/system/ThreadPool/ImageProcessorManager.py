import os
import threading
from PIL import Image
import os

class ImageProcessingManager:
    def __init__(self, upload_folder, ImageColorAnalyzer, GetMetadata, ImageFeatureExtractor, process_top_features):
        self.upload_folder = upload_folder
        self.ImageColorAnalyzer = ImageColorAnalyzer
        self.GetMetadata = GetMetadata
        self.ImageFeatureExtractor = ImageFeatureExtractor
        self.threads = []
        self.process_top_features = process_top_features

    def process_image(self, filename):
        # Construct the full path
        filepath = os.path.join(self.upload_folder, filename)
        self.analyze_colors(filepath)
        self.extract_features(filepath)

    def analyze_colors(self, filepath):
        analyzer = self.ImageColorAnalyzer(filepath)
        analyzer.full_color_analysis()
        # Add your color analysis logic here

    def extract_features(self, filepath):
        feature_extractor = self.ImageFeatureExtractor(self.process_top_features)
        feature_extractor.get_features(filepath)
        # Add your feature extraction logic here

    def wait_for_completion(self):
        # Wait for all threads to finish
        for thread in self.threads:
            thread.join()




# Usage example (in your Flask route):

# You would pass the actual classes during initialization
# image_manager = ImageProcessingManager(
#     upload_folder='path_to_upload_folder',
#     ImageColorAnalyzer=YourImageColorAnalyzerClass,
#     GetMetadata=YourGetMetadataClass,
#     ImageFeatureExtractor=YourImageFeatureExtractorClass
# )

# For each valid file:
# image_manager.process_image(file)

# After processing all images:
# image_manager.wait_for_completion()
