''' 
File Information:
File Name: Name of the image file.
File Size: Size of the file (in bytes).
File Type: Format (e.g., JPEG, PNG, TIFF).
Creation Date/Time: When the image file was created.
Last Modified Date/Time: When the file was last modified.

EXIF Data (Exchangeable Image File Format):
Camera Make and Model: The camera brand and model that took the picture.
Lens Info: Information about the lens used.
Focal Length: The focal length of the lens when the image was captured.
Exposure Time (Shutter Speed): The amount of time the camera's shutter was open.
Aperture: The size of the lens opening (f-stop).
ISO Speed: Sensitivity of the camera sensor.
GPS Coordinates: Geolocation where the image was taken.
Orientation: Image rotation data (landscape/portrait).
Flash: Whether the flash was fired.

Image Resolution & Dimensions:
Image Width and Height: Pixel dimensions of the image.
Resolution: DPI (dots per inch), describing the image's printing quality.

Color Information:
Color Profile: The color model (e.g., RGB, CMYK).
Bit Depth: Number of bits used to represent each color channel.
Software Information:

Software: The software used to process or edit the image.
'''


from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import pandas as pd

def GetMetadata(imagelink):
    metadata = []
    try:
        # Open image
        image = Image.open(imagelink)
        
        # File Information
        metadata.append({
            "filename": imagelink,
            "feature_type": "Metadata",
            "feature_value": "File Name",
            "probability": os.path.basename(imagelink) or ""  # Handle empty filename
        })
        metadata.append({
            "filename": imagelink,
            "feature_type": "Metadata",
            "feature_value": "File Size (bytes)",
            "probability": os.path.getsize(imagelink) if os.path.exists(imagelink) else 0 # Handle non-existent file
        })
        metadata.append({
            "filename": imagelink,
            "feature_type": "Metadata",
            "feature_value": "File Type",
            "probability": image.format or ""  # Handle missing format
        })
        
        # EXIF Data
        exif_data = image._getexif()
        if exif_data:
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)

                # Handle NaN or None values
                if value is None or (isinstance(value, float) and pd.isna(value)):  
                    value = ""

                # Use switch-case (dict approach in Python)
                tag_switch = {
                    "DateTimeOriginal": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "Creation Date/Time", "probability": value or ""}),
                    "DateTime": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "Last Modified Date/Time", "probability": value or ""}),
                    "Make": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "Camera Make", "probability": value or ""}),
                    "Model": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "Camera Model", "probability": value or ""}),
                    "FocalLength": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "Focal Length", "probability": value or ""}),
                    "ExposureTime": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "Exposure Time (Shutter Speed)", "probability": value or ""}),
                    "FNumber": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "Aperture", "probability": value or ""}),
                    "ISOSpeedRatings": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "ISO Speed", "probability": value or ""}),
                    "Flash": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "Flash", "probability": value or ""}),
                    "GPSInfo": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "GPS Coordinates", "probability": {GPSTAGS.get(k, k): (v or "") for k, v in value.items()}}), # Handle None in GPSInfo
                    "Orientation": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "Orientation", "probability": value or ""}),
                }
                
                # Execute the corresponding function if tag_name exists in the dictionary
                tag_switch.get(tag_name, lambda: None)()

        # Image Resolution & Dimensions
        metadata.append({
            "filename": imagelink,
            "feature_type": "Metadata",
            "feature_value": "Image Width",
            "probability": image.size[0] if image.size else 0  # Handle missing size
        })
        metadata.append({
            "filename": imagelink,
            "feature_type": "Metadata",
            "feature_value": "Image Height",
            "probability": image.size[1] if image.size else 0  # Handle missing size
        })
        metadata.append({
            "filename": imagelink,
            "feature_type": "Metadata",
            "feature_value": "Resolution",
            "probability": image.info.get("dpi", "") or ""  # Handle missing DPI
        })

        # Color Information
        metadata.append({
            "filename": imagelink,
            "feature_type": "Metadata",
            "feature_value": "Color Profile",
            "probability": image.info.get("icc_profile", "") or ""  # Handle missing color profile
        })
        metadata.append({
            "filename": imagelink,
            "feature_type": "Metadata",
            "feature_value": "Bit Depth",
            "probability": image.mode or "" # Handle missing bit depth
        })
        
        # Software Information
        metadata.append({
            "filename": imagelink,
            "feature_type": "Metadata",
            "feature_value": "Software",
            "probability": image.info.get("software", "") or ""  # Handle missing software info
        })
        
    except Exception as e:
        metadata.append({
            "filename": imagelink,
            "feature_type": "Error",
            "feature_value": "Error Message",
            "probability": str(e)
        })
    print(metadata)
    return metadata