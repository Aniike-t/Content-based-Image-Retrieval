# --- START OF FILE ImageProcessorManager.py --- (Corrected)

import os
import threading
from PIL import Image

class ImageProcessingManager:
    def __init__(self, upload_folder, ImageColorAnalyzer, GetMetadata, ImageFeatureExtractor, process_top_features, cursor, conn):
        self.upload_folder = upload_folder
        self.ImageColorAnalyzer = ImageColorAnalyzer
        self.GetMetadata = GetMetadata
        self.ImageFeatureExtractor = ImageFeatureExtractor
        self.process_top_features = process_top_features
        self.cursor = cursor
        self.conn = conn
        self.results = []
        self.lock = threading.Lock()
        self.threads = []

    def process_image(self, base_filename):
        filepath = os.path.join(self.upload_folder, base_filename)
        thread = threading.Thread(target=self.image_processing_thread, args=(filepath, base_filename)) # Pass base_filename
        self.threads.append(thread)
        thread.start()

    def image_processing_thread(self, filepath, base_filename):  # Add base_filename parameter
        try:
            res1 = self.analyze_colors(filepath)
            res2 = self.get_metadata(filepath)
            res3 = self.extract_features(filepath)

            # Use lock to safely append results
            with self.lock:
                self.results.append((base_filename, res1, res2, res3))  # Store base_filename

        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    def analyze_colors(self, filepath):
        analyzer = self.ImageColorAnalyzer(filepath)
        return analyzer.full_color_analysis()

    def get_metadata(self, filepath):
        return self.GetMetadata(filepath)

    def extract_features(self, filepath):
        feature_extractor = self.ImageFeatureExtractor(self.process_top_features)
        return feature_extractor.get_features(filepath)

    def insert_data(self):
        with self.lock:
            for base_filename, res1, res2, res3 in self.results:  # Unpack base_filename
                if not base_filename:  # Skip if base_filename is empty
                    continue

                # Insert color analysis data
                for item in res1:
                    try:
                        self.cursor.execute('''
                            INSERT INTO Imagefeatures (filename, feature_type, feature_value, probability)
                            VALUES (?, ?, ?, ?)
                        ''', (base_filename, item['feature_type'], str(item['feature_value']), float(item['probability'])))
                    except (ValueError, TypeError) as e:
                        print(f"Error inserting color data for {base_filename}: {e}")
                        continue  # Skip to the next item

                # Insert metadata
                for item in res2:
                    try:
                        self.cursor.execute('''
                            INSERT INTO Imagefeatures (filename, feature_type, feature_value, probability)
                            VALUES (?, ?, ?, ?)
                        ''', (base_filename, item['feature_type'], str(item['feature_value']), float(item['probability'])))
                    except (ValueError, TypeError) as e:
                        print(f"Error inserting metadata for {base_filename}: {e}")
                        continue  # Skip

                # Insert feature extraction data
                for item in res3:
                    try:
                        self.cursor.execute('''
                            INSERT INTO Imagefeatures (filename, feature_type, feature_value, probability)
                            VALUES (?, ?, ?, ?)
                        ''', (base_filename, item['feature_type'], str(item['feature_value']), float(item['probability'])))
                    except (ValueError, TypeError) as e:
                        print(f"Error inserting feature data for {base_filename}: {e}")
                        continue

            self.conn.commit()


    def wait_for_completion(self):
        for thread in self.threads:
            thread.join()
        self.insert_data()