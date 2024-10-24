import os
import threading
import random
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
        self.results = []  # Store results from all threads
        self.lock = threading.Lock()  # Lock for thread safety
        self.threads = []

    def process_image(self, filename):
        # Construct the full path
        filepath = os.path.join(self.upload_folder, filename)
        thread = threading.Thread(target=self.image_processing_thread, args=(filepath,))
        self.threads.append(thread)
        thread.start()

    def image_processing_thread(self, filepath):
        try:
            res1 = self.analyze_colors(filepath)
            res2 = self.get_metadata(filepath)
            res3 = self.extract_features(filepath)

            # Use lock to safely append results
            with self.lock:
                self.results.append((res1, res2, res3))
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    def analyze_colors(self, filepath):
        analyzer = self.ImageColorAnalyzer(filepath)
        return analyzer.full_color_analysis()  # Return the results

    def get_metadata(self, filepath):
        return self.GetMetadata(filepath)  # Return the results
    
    def extract_features(self, filepath):
        feature_extractor = self.ImageFeatureExtractor(self.process_top_features)
        return feature_extractor.get_features(filepath)  # Return the results

    def insert_data(self):
        with self.lock:  # Lock for thread-safe database insertion
            for res1, res2, res3 in self.results:
                # Insert color analysis (res1) data
                for item in res1:
                    self.cursor.execute(''' 
                        INSERT INTO Imagefeatures (filename, feature_type, feature_value, probability)
                        VALUES (?, ?, ?, ?)
                    ''', (item['filename'], item['feature_type'], str(item['feature_value']), item['probability']))

                # Insert metadata (res2) data
                for item in res2:
                    self.cursor.execute(''' 
                        INSERT INTO Imagefeatures (filename, feature_type, feature_value, probability)
                        VALUES (?, ?, ?, ?)
                    ''', (item['filename'], item['feature_type'], str(item['feature_value']), item['probability']))

                # Insert feature extraction (res3) data
                for item in res3:
                    self.cursor.execute(''' 
                        INSERT INTO Imagefeatures (filename, feature_type, feature_value, probability)
                        VALUES (?, ?, ?, ?)
                    ''', (item['filename'], item['feature_type'], str(item['feature_value']), item['probability']))
            
            # Commit the changes
            self.conn.commit()
            print("Done with file processing - " + str(random.randint(100000, 999999)))

    def wait_for_completion(self):
        # Wait for all threads to finish
        for thread in self.threads:
            thread.join()
        
        # After all threads are done, insert data into the database
        self.insert_data()

# Usage example (in your Flask route):
# image_manager = ImageProcessingManager(
#     upload_folder='path_to_upload_folder',
#     ImageColorAnalyzer=YourImageColorAnalyzerClass,
#     GetMetadata=YourGetMetadataClass,
#     ImageFeatureExtractor=YourImageFeatureExtractorClass,
#     process_top_features=YourProcessTopFeatures,
#     cursor=your_database_cursor,
#     conn=your_database_connection
# )

# For each valid file:
# image_manager.process_image(file)

# After processing all images:
# image_manager.wait_for_completion()