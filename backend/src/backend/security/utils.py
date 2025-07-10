import secrets
import base64


def generate_service_token(prefix: str = ""):
    random_bytes = secrets.token_bytes(64)

    service_key = base64.urlsafe_b64encode(random_bytes).decode("utf-8")
    service_key = f"{prefix}_{service_key}"

    return service_key
