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
                    "feature_type": item['feature_type'],
                    "feature_value": value,
                    "probability": item['probability']
                })
        return processed_data

    def get_features(self, filename):
        try:
            img = Image.open(filename).convert("RGB")
        except Exception as e:
            print(f"Error opening image {filename}: {e}")
            return []

        # Process the image
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
                "feature_type": "Image classification",
                "feature_value": self.model.config.id2label[top5_catid[i].item()],
                "probability": round(top5_prob[i].item(), 4)
            })

        processed_feature_list = self.split_multiword_features(feature_list)
        processed_feature_list_extra = self.process_top_features(processed_feature_list)

        # Combine processed features
        processed_feature_list_added = processed_feature_list + processed_feature_list_extra
        print(processed_feature_list_added)
        return processed_feature_list_added