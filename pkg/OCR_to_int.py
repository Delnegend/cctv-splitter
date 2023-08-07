import sys

import cv2
import numpy as np
import pytesseract


def OCR_to_int(nparray: np.ndarray) -> int:
    """Converts an image to text and returns the integer value"""
    # convert to grayscale
    gray = cv2.cvtColor(nparray, cv2.COLOR_BGR2GRAY)

    # gaussian blur to remove noise
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    # sharpen the image
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    sharpen = cv2.filter2D(blur, -1, kernel)

    # upscale the image x4 to make it easier to read using lanczos-3
    sharpen = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_LANCZOS4)

    result = sharpen

    ocr_result: str = pytesseract.image_to_string(result, config="--psm 7 -c tessedit_char_whitelist=0123456789").strip()

    # save ocr_result to a file with filename as the frame number, overwrite if it already exists
    # if os.path.exists(f"{ocr_result}.png"):
    #     os.remove(f"{ocr_result}.png")
    # cv2.imwrite(f"{ocr_result}.png", result)

    # print("OCR result:", ocr_result)
    if ocr_result == "":
        print("OCR failed to read the image")
        cv2.imwrite("error.png", result)
        sys.exit(1)
    return int(ocr_result)
