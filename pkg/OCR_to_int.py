import pytesseract
import numpy as np

def OCR_to_int(nparray: np.ndarray) -> int:
    """Converts an image to text and returns the integer value"""
    return int(pytesseract.image_to_string(nparray, config="--psm 7 -c tessedit_char_whitelist=0123456789").strip())