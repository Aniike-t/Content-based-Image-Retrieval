from PIL import Image
import io

def is_valid_image(file_stream):
    try:
        image = Image.open(file_stream)
        image.verify()
        return True
    except (IOError, SyntaxError):
        return False