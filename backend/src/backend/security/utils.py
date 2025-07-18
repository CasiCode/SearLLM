"""a collection of security utilities used in the application"""

import secrets
import base64


def generate_service_token(prefix: str = "", length: int = 64) -> str:
    """
    Generates a strong service token with 64 UTF-8 characters.

    Parameters:
        prefix (str): a prefix to be added before the token
        length (int): token length in characters

    Returns:
        str token, len(prefix)+length+1 characters long in format:
        prefix_token

    """
    random_bytes = secrets.token_bytes(length)

    service_token = base64.urlsafe_b64encode(random_bytes).decode("utf-8")
    service_token = f"{prefix}_{service_token}"

    return service_token
