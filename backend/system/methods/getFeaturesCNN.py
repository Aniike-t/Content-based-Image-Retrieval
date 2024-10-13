from transformers import AutoImageProcessor, AutoModelForImageClassification
import torch
from PIL import Image
import os

class ImageFeatureExtractor:
    def __init__(self, 
                 process_top_features,
                 processor_path='D:/Github Local Repos/CBIR/backend/system/methods/downloadModel/model/local_vit_processor', 
                 model_path='D:/Github Local Repos/CBIR/backend/system/methods/downloadModel/model/local_vit_model', 
                 predictionUpto=5):
        # Check if the processor and model paths exist
        if not os.path.exists(processor_path):
            raise FileNotFoundError(f"Processor path not found: {processor_path}")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model path not found: {model_path}")

        # Load processor and model using Auto classes
        self.processor = AutoImageProcessor.from_pretrained(processor_path)
        self.model = AutoModelForImageClassification.from_pretrained(model_path)
        self.predictionUpto = predictionUpto
        self.process_top_features = process_top_features

    def split_multiword_features(self, feature_data):
        processed_data = []
        for item in feature_data:
            values = [value.strip() for value in item['feature_value'].split(',')]
            for value in values:
                processed_data.append({
                    "filename": item['filename'],
                    "region": item.get('region', "Original"),
                    "feature_type": item['feature_type'],
                    "feature_value": value,
                    "probability": item['probability']
                })
        return processed_data

    def extract_features_from_image(self, img, filename, region_name="Original"):
        inputs = self.processor(images=img, return_tensors="pt")
        
        with torch.no_grad():  # Disable gradient calculation
            outputs = self.model(**inputs)
        logits = outputs.logits

        probabilities = torch.softmax(logits, dim=-1)[0]
        top5_prob, top5_catid = torch.topk(probabilities, self.predictionUpto)

        feature_list = []
        for i in range(top5_prob.size(0)):
            feature_list.append({
                "filename": filename,
                "region": region_name,
                "feature_type": "Image classification",
                "feature_value": self.model.config.id2label[top5_catid[i].item()],
                "probability": round(top5_prob[i].item(), 4)
            })

        return feature_list

    def get_quadrant_images(self, img):
        width, height = img.size
        mid_x, mid_y = width // 2, height // 2

        quadrants = {
            "Top Left": img.crop((0, 0, mid_x, mid_y)),
            "Top Right": img.crop((mid_x, 0, width, mid_y)),
            "Bottom Left": img.crop((0, mid_y, mid_x, height)),
            "Bottom Right": img.crop((mid_x, mid_y, width, height)),
        }
        return quadrants

    def adjust_probabilities(self, original_features, quadrant_features):
        for q_feature in quadrant_features:
            # Apply 0.75 multiplier for quadrant features
            q_feature['probability'] *= 0.75
            for o_feature in original_features:
                # If feature value matches, apply 1.25 multiplier
                if q_feature['feature_value'] == o_feature['feature_value']:
                    q_feature['probability'] *= 1.25
        return quadrant_features

    def get_features(self, filename):
        try:
            img = Image.open(filename).convert("RGB")
        except Exception as e:
            print(f"Error opening image {filename}: {e}")
            return []

        # Extract features from the original image
        original_features = self.extract_features_from_image(img, filename, "Original")

        # Get features from quadrants
        quadrants = self.get_quadrant_images(img)
        all_features = original_features.copy()
        for quadrant_name, quadrant_img in quadrants.items():
            quadrant_features = self.extract_features_from_image(quadrant_img, filename, quadrant_name)
            adjusted_quadrant_features = self.adjust_probabilities(original_features, quadrant_features)
            all_features += adjusted_quadrant_features

        processed_feature_list = self.split_multiword_features(all_features)
        processed_feature_list_extra = self.process_top_features(processed_feature_list)

        # Combine processed features
        processed_feature_list_added = processed_feature_list + processed_feature_list_extra
        print(processed_feature_list_added)
        return processed_feature_list_added