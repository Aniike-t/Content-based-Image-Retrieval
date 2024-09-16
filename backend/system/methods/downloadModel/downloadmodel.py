from transformers import ViTImageProcessor, ViTForImageClassification
import torch
from PIL import Image

# Step 1: Download the model and processor and save them locally
processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224')

# Save the model and processor to a local directory
model.save_pretrained('./model/local_vit_model')
processor.save_pretrained('./model/local_vit_processor')