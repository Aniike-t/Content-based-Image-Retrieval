from transformers import AutoImageProcessor, AutoModelForImageClassification
import torch
from PIL import Image
import os

# Step 1: Download the model and processor and save them locally
model_name = "google/vit-base-patch16-224"

# Download and save model locally
processor = AutoImageProcessor.from_pretrained(model_name)
model = AutoModelForImageClassification.from_pretrained(model_name)

# Save the model and processor to a local directory
model.save_pretrained('./model/local_vit_model')
processor.save_pretrained('./model/local_vit_processor')

# Step 2: Load the model and processor from local directory
local_processor = AutoImageProcessor.from_pretrained('./model/local_vit_processor')
local_model = AutoModelForImageClassification.from_pretrained('./model/local_vit_model')
