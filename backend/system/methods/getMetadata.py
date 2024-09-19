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
            "probability/value": os.path.basename(imagelink)
        })
        metadata.append({
            "filename": imagelink,
            "feature_type": "Metadata",
            "feature_value": "File Size (bytes)",
            "probability/value": os.path.getsize(imagelink)
        })
        metadata.append({
            "filename": imagelink,
            "feature_type": "Metadata",
            "feature_value": "File Type",
            "probability/value": image.format
        })
        
        # EXIF Data
        exif_data = image._getexif()
        if exif_data:
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                
                # Use switch-case (dict approach in Python)
                tag_switch = {
                    "DateTimeOriginal": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "Creation Date/Time", "probability/value": value}),
                    "DateTime": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "Last Modified Date/Time", "probability/value": value}),
                    "Make": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "Camera Make", "probability/value": value}),
                    "Model": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "Camera Model", "probability/value": value}),
                    "FocalLength": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "Focal Length", "probability/value": value}),
                    "ExposureTime": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "Exposure Time (Shutter Speed)", "probability/value": value}),
                    "FNumber": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "Aperture", "probability/value": value}),
                    "ISOSpeedRatings": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "ISO Speed", "probability/value": value}),
                    "Flash": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "Flash", "probability/value": value}),
                    "GPSInfo": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "GPS Coordinates", "probability/value": {GPSTAGS.get(k, k): v for k, v in value.items()}}),
                    "Orientation": lambda: metadata.append({"filename": imagelink, "feature_type": "Metadata", "feature_value": "Orientation", "probability/value": value}),
                }
                
                # Execute the corresponding function if tag_name exists in the dictionary
                tag_switch.get(tag_name, lambda: None)()

        # Image Resolution & Dimensions
        metadata.append({
            "filename": imagelink,
            "feature_type": "Metadata",
            "feature_value": "Image Width",
            "probability/value": image.size[0]
        })
        metadata.append({
            "filename": imagelink,
            "feature_type": "Metadata",
            "feature_value": "Image Height",
            "probability/value": image.size[1]
        })
        metadata.append({
            "filename": imagelink,
            "feature_type": "Metadata",
            "feature_value": "Resolution",
            "probability/value": image.info.get("dpi", "Unknown")
        })

        # Color Information
        metadata.append({
            "filename": imagelink,
            "feature_type": "Metadata",
            "feature_value": "Color Profile",
            "probability/value": image.info.get("icc_profile", "Unknown")
        })
        metadata.append({
            "filename": imagelink,
            "feature_type": "Metadata",
            "feature_value": "Bit Depth",
            "probability/value": image.mode
        })
        
        # Software Information
        metadata.append({
            "filename": imagelink,
            "feature_type": "Metadata",
            "feature_value": "Software",
            "probability/value": image.info.get("software", "Unknown")
        })
        
    except Exception as e:
        metadata.append({
            "filename": imagelink,
            "feature_type": "Error",
            "feature_value": "Error Message",
            "probability/value": str(e)
        })
    print(metadata)
    return metadata
  
  
GetMetadata('backend/system/methods/HMD_Nokia_8.3_5G_hdr.jpg')