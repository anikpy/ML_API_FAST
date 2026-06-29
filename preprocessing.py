import numpy as np
import cv2
import imghdr
import math
from typing import List


def compress_image(image_bytes: List[bytes]) -> np.ndarray:
    threshold = 4000000
    if len(image_bytes) > threshold:
        # checking the image format
        image_type = imghdr.what(None, image_bytes)
        target_filesize = 2000000
        quality = 50
        nid_nparray = np.asarray(bytearray(image_bytes), dtype="uint8")
        nid = cv2.imdecode(nid_nparray, cv2.IMREAD_COLOR)
        while True:
            if image_type == "jpeg":
                params = [cv2.IMWRITE_JPEG_QUALITY, quality]
                result, encoded_img = cv2.imencode(".jpg", nid, params)
            elif image_type == "png":
                params = [cv2.IMWRITE_PNG_COMPRESSION, int(math.ceil(quality / 10))]
                result, encoded_img = cv2.imencode(".png", nid, params)
            else:
                raise ValueError(f"Unsupported image format: {image_type}")

            # check for the desired filesize
            if encoded_img.nbytes <= target_filesize:
                break
            quality = max(quality - 5, 5)
        return encoded_img
    # return nid_nparray
