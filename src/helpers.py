import base64


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
