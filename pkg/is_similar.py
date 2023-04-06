import cv2
import numpy as np
from main import SENSITIVITY
from skimage.metrics import structural_similarity as ssim

def is_similar(imageA: np.ndarray, imageB: np.ndarray) -> bool:
    """Using SSIM to determine if two images are similar"""
    imageA_gray = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    imageB_gray = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    (score, diff) = ssim(imageA_gray, imageB_gray, full=True)
    diff = (diff * 255).astype("uint8")
    return score > SENSITIVITY