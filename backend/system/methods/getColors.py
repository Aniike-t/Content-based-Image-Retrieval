import cv2
import numpy as np
from sklearn.cluster import KMeans

class ImageColorAnalyzer:
    def __init__(self, filename, num_clusters=5):
        """
        Initialize with image filename and number of clusters for dominant color detection.
        :param filename: path to the image
        :param num_clusters: number of dominant colors to detect using K-means (default: 5)
        """
        self.filename = filename
        self.image = cv2.imread(filename)
        self.hsv_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        self.num_clusters = num_clusters

        # Define basic color ranges (Hue values) for fast analysis
        self.basic_color_ranges = {
            "Red": [(0, 10), (160, 180)],  # Two ranges for red
            "Orange": [(11, 25)],
            "Yellow": [(26, 35)],
            "Green": [(36, 85)],
            "Blue": [(86, 125)],
            "Purple": [(126, 145)],
            "Brown": [(146, 160)]
        }
        
        # Extended color palette (more detailed hues for deeper analysis)
        self.extended_color_names = [
            "Light Red", "Dark Red", "Light Orange", "Dark Orange",
            "Light Yellow", "Dark Yellow", "Light Green", "Dark Green",
            "Light Blue", "Dark Blue", "Light Purple", "Dark Purple", "Brown"
        ]

    def calculate_histogram(self):
        """
        Calculate and normalize the color histogram in the HSV color space.
        :return: Flattened and normalized histogram.
        """
        hist = cv2.calcHist([self.hsv_image], [0], None, [180], [0, 180])
        hist = cv2.normalize(hist, hist).flatten()
        return hist

    def analyze_colors_basic(self):
        """
        Analyze the image using the basic color palette for a faster result.
        :return: List of colors with their percentage in the image.
        """
        hist = self.calculate_histogram()
        total_pixels = np.sum(hist)
        results = []

        for color_name, ranges in self.basic_color_ranges.items():
            color_percentage = 0
            for (low, high) in ranges:
                color_percentage += np.sum(hist[low:high + 1])

            color_percentage = (color_percentage / total_pixels)
            if color_percentage > 0:
                results.append({
                    "filename": self.filename,
                    "feature_type": "Colors",
                    "feature_value": color_name,
                    "probability": round(color_percentage, 2)
                })
        
        return results

    def analyze_dominant_colors(self):
        """
        Use K-means clustering to find the most dominant colors in the image.
        :return: List of dominant colors with their percentages in the image.
        """
        # Reshape image to a list of pixels
        pixels = self.image.reshape(-1, 3)
        
        # Apply K-means clustering to find dominant colors
        kmeans = KMeans(n_clusters=self.num_clusters)
        kmeans.fit(pixels)
        colors = kmeans.cluster_centers_.astype(int)
        labels = kmeans.labels_

        # Count the frequency of each cluster (color)
        label_counts = np.bincount(labels)
        total_count = len(labels)

        # Get color percentages
        color_percentages = label_counts / total_count

        results = []
        for i in range(self.num_clusters):
            color_value = colors[i].tolist()
            results.append({
                "filename": self.filename,
                "feature_type": "Dominant Colors",
                "feature_value": color_value,
                "probability": round(color_percentages[i] , 4)
            })
        
        return results

    def analyze_colors_extended(self):
        """
        Analyze the image using an extended color palette for deeper color extraction.
        :return: List of detailed color percentages.
        """
        hist = self.calculate_histogram()
        total_pixels = np.sum(hist)
        results = []

        # Extended color ranges can be set up in a similar way, or use clustering
        # This is an area where you might define more nuanced hues

        # Example: Just returning basic results (can be extended further)
        results.extend(self.analyze_colors_basic())
        
        return results

    def full_color_analysis(self):
        """
        Perform both basic and dominant color analysis for best performance.
        :return: Combined list of basic and dominant colors.
        """
        basic_colors = self.analyze_colors_basic()
        dominant_colors = self.analyze_dominant_colors()
        
        return basic_colors + dominant_colors

# Example usage

# analyzer = ImageColorAnalyzer("backend/system/methods/carparkedneartree.jpeg", num_clusters=5)
# color_info = analyzer.full_color_analysis()
# print(color_info)
