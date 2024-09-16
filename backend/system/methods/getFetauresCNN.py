import sys
import os

''' temproray fix for the import error '''
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.system.tokenisation.wordnetExtraction import process_top_features
from PIL import Image
from transformers import ViTImageProcessor, ViTForImageClassification
import torch

class ImageFeatureExtractor:
    def __init__(self, processor_path, model_path, predictionUpto=6):
        self.processor = ViTImageProcessor.from_pretrained(processor_path)
        self.model = ViTForImageClassification.from_pretrained(model_path)
        self.predictionUpto = predictionUpto

    def split_multiword_features(self, feature_data):
        processed_data = []
        for item in feature_data:
            # Split the feature_value by commas and strip any leading/trailing spaces
            values = [value.strip() for value in item['feature_value'].split(',')]
            # Create a new entry for each split word
            for value in values:
                processed_data.append({
                    "filename": item['filename'],
                    "feature_type": item['feature_type'],
                    "feature_value": value,
                    "probability": item['probability']
                })
        return processed_data

    def get_features(self, filename):
        img = Image.open(filename)
        
        # Preprocess image and get model output
        inputs = self.processor(images=img, return_tensors="pt")
        outputs = self.model(**inputs)
        logits = outputs.logits

        # Get the top predicted class and its probability
        probabilities = torch.softmax(logits, dim=-1)[0]
        top5_prob, top5_catid = torch.topk(probabilities, self.predictionUpto)

        # Collect feature list
        feature_list = []
        for i in range(top5_prob.size(0)):
            feature_list.append({
                "filename": filename,
                "feature_type": "Image classification",
                "feature_value": self.model.config.id2label[top5_catid[i].item()],
                "probability": round(top5_prob[i].item(), 4)
            })
        
        # Process multi-word features
        processed_feature_list = self.split_multiword_features(feature_list)
        print(len(processed_feature_list))
        
        
        ''' Process top features to find synonyms and adjust probabilities. '''
        processed_feature_list_extra = process_top_features(processed_feature_list)
        print(len(processed_feature_list_extra))
        
        ''' Added list of processed features '''
        processed_feature_list_added = processed_feature_list + processed_feature_list_extra
        print(len(processed_feature_list_added))
        
        # Output the result
        print(processed_feature_list_added)
        return processed_feature_list_added


# extractor = ImageFeatureExtractor('backend/system/methods/downloadModel/model/local_vit_processor', 'backend/system/methods/downloadModel/model/local_vit_model')
# extractor.get_features('backend/system/methods/carneaartree.webp')
