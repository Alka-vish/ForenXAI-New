import io
from pathlib import Path
from typing import Tuple, Dict, Any

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError
from fastapi import UploadFile, HTTPException, status

from utils.image_utils import ALLOWED_EXTENSIONS


async def validate_and_read_image(image: UploadFile) -> Tuple[bytes, str]:
    """
    Validates the uploaded file presence, extension, and loads raw bytes into memory.
    Raises HTTPException(400) for missing, invalid extension, or empty files.
    """
    if not image or not image.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing image file. Please provide an image to analyze.",
        )

    ext = Path(image.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{ext}'. Only JPG, JPEG, PNG, and WEBP are supported.",
        )

    try:
        contents = await image.read()
    except Exception as read_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file: {str(read_err)}",
        )

    if not contents or len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    return contents, ext


def load_pil_image(contents: bytes, ext: str) -> Tuple[Image.Image, str, str, int, int]:
    """
    Verifies and decodes image bytes using Pillow.
    Returns (pil_image, color_mode, img_format, width, height).
    """
    try:
        pil_image = Image.open(io.BytesIO(contents))
        pil_image.verify()  # Verifies file integrity
        # Re-open because verify() closes or invalidates file pointer
        pil_image = Image.open(io.BytesIO(contents))
        color_mode = str(pil_image.mode)
        img_format = str(pil_image.format or ext.replace(".", "").upper())
        width, height = pil_image.size
        return pil_image, color_mode, img_format, int(width), int(height)
    except (UnidentifiedImageError, OSError, SyntaxError) as pil_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Corrupted or invalid image file: {str(pil_err)}",
        )


def load_cv_image(contents: bytes) -> Tuple[np.ndarray, np.ndarray, int]:
    """
    Decodes image bytes into OpenCV BGR matrix and grayscale representation.
    Returns (cv_img, gray, total_pixels).
    """
    np_buffer = np.frombuffer(contents, dtype=np.uint8)
    cv_img = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)

    if cv_img is None or cv_img.size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to decode image pixels. The image may be corrupted or invalid.",
        )

    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    total_pixels = int(gray.size)
    return cv_img, gray, total_pixels


def extract_image_information(
    filename: str, width: int, height: int, color_mode: str, img_format: str, file_size_bytes: int
) -> Dict[str, Any]:
    """
    Constructs the image_information dictionary.
    """
    return {
        "filename": filename,
        "width": width,
        "height": height,
        "color_mode": color_mode,
        "format": img_format,
        "file_size_bytes": file_size_bytes,
    }
