import base64
import os


def base64_encode(data: bytes) -> str:
    """
    Encodes data (bytes) using the base 64 encoding.
    """
    return base64.b64encode(data).decode("utf-8")


def base64_decode(encoded_str: str) -> bytes:
    """
    Decodes a base64-encoded string back into bytes.
    """
    return base64.b64decode(encoded_str)


def save_b64_image(b64_image: str, filepath: str = "image.png"):
    """
    Saves a base64-encoded string as an image.

    Args:
        b64_image (str)
        filepath (str): path where the image should be saved. Defaults to image.png.
    """
    image_data = base64.b64decode(b64_image)
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(image_data)
    return filepath
